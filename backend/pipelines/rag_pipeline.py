"""
backend/pipelines/rag_pipeline.py

Implements the Retrieval-Augmented Generation (RAG) pipeline.
Orchestrates context building, semantic retrieval, and LLM generation via ProviderFactory.
"""

import logging
from backend.rag.retriever import get_retriever, Retriever
from backend.providers.provider_factory import get_provider
from backend.context.student_context_builder import StudentContextBuilder
# Assuming we match the PipelineResult import from the existing resume_match_pipeline.py
from backend.services.pipeline_dispatcher import PipelineResult

logger = logging.getLogger(__name__)

class RagPipeline:
    def __init__(self, provider_factory_func=None, retriever: Retriever = None):
        """
        Initialize the RagPipeline.
        Dependencies are injected for testability, falling back to singletons.
        """
        self.get_provider = provider_factory_func or get_provider
        self.retriever = retriever or get_retriever()
        self.context_builder = StudentContextBuilder()

    def execute(self, user_id: str, query: str, **kwargs) -> PipelineResult:
        """
        Execute the RAG pipeline.
        Signature matches the existing execute() pattern in this directory's pipelines.
        """
        # Step 3a: Build student context
        student_context = self.context_builder.build(user_id)
        
        # Step 3b: Rewrite/expand query using context
        # Append academic framing to the query used for retrieval without mutating the user-facing query
        expanded_query = query
        if student_context.weak_subjects:
            expanded_query = f"{query} (focus on fundamentals for {', '.join(student_context.weak_subjects)})"
            
        # Step 3c: Call retriever
        chunks = []
        try:
            chunks = self.retriever.retrieve_with_fallback(user_id, expanded_query, top_k=5)
        except Exception as e:
            logger.error("RAG retrieval failed for user %s: %s", user_id, e, exc_info=True)
            # Fall back gracefully; chunks remain empty
            
        # Step 3d & 3e: Handle chunks and build system prompt
        if not chunks:
            logger.info("No context found for query: %s. Falling back to general knowledge.", query)
            used_rag = False
            sources = []
            context_block = ""
            instruction = "Answer the user's question directly based on your general knowledge."
        else:
            used_rag = True
            sources = list(set([c.doc_name for c in chunks]))
            context_block = self.retriever.format_for_llm_context(chunks)
            instruction = (
                "Using the context provided below, write a clear, complete answer to the student's question. "
                "Synthesize information across all provided context sections rather than quoting or restating "
                "any single section verbatim. Do not mention document names, file names, or the word 'source' "
                "in your answer — source attribution is handled separately by the system."
            )
            
        system_prompt = (
            f"You are a personalized academic assistant.\n\n"
            f"User Profile:\n{student_context.to_prompt_context()}\n\n"
            f"{instruction}\n\n"
        )
        
        if context_block:
            system_prompt += f"Context Documents:\n{context_block}\n"
            
        # Step 3f: Call the provider via provider_factory
        generation_error = None

        try:
            # We use the default fallback provider if "rag" isn't strictly defined in the factory mapping
            provider = self.get_provider("rag") 
            # The generate method returns an AIResult per the base_provider.py contract
            ai_result = provider.generate(prompt=query, system=system_prompt)
            answer_text = ai_result.content
        except Exception as e:
            logger.error("LLM generation failed in RAG pipeline for user %s: %s", user_id, e, exc_info=True)
            answer_text = "I'm sorry, I encountered an error while trying to generate an answer."
            generation_error = str(e)

        # Step 3g: Return a PipelineResult with metadata
        metadata = {
            "used_rag": used_rag,
            "sources": sources if chunks else [],
            "chunk_count": len(chunks)
        }
        if generation_error:
            metadata["generation_error"] = generation_error
        
        return PipelineResult(
            response=answer_text,
            data=metadata
        )
