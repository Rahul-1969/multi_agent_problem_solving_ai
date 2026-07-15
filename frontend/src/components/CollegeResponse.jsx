import React, { useState } from 'react';
import { MapPin, Globe, Copy, Check, Bookmark, BookmarkCheck } from 'lucide-react';
import './CollegeResponse.css';

const formatLPA = (val) => val ? `₹${val} LPA` : 'N/A';

const TIER_CONFIG = {
  SAFE:     { dot: '#10b981', label: 'SAFE',     stars: '★★★★★ Highly Recommended' },
  MODERATE: { dot: '#f59e0b', label: 'MODERATE', stars: '★★★★☆ Good Match' },
  DREAM:    { dot: '#ef4444', label: 'DREAM',    stars: '★★★☆☆ Reach School' },
};

// Deterministic gradient from college code
const codeToGradient = (code = '') => {
  let h = 0;
  for (let i = 0; i < code.length; i++) h = code.charCodeAt(i) + ((h << 5) - h);
  const hue = Math.abs(h) % 360;
  return `linear-gradient(135deg, hsl(${hue},60%,30%), hsl(${(hue + 40) % 360},50%,20%))`;
};

const CopyButton = ({ text }) => {
  const [copied, setCopied] = useState(false);
  const handleCopy = () => {
    navigator.clipboard.writeText(text).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 1800);
    });
  };
  return (
    <button className="copy-btn" onClick={handleCopy} title="Copy college code">
      {copied ? <Check size={13} /> : <Copy size={13} />}
    </button>
  );
};

import { useChatStore } from '../store';
import apiService from '../services/apiService';
import useToastStore from '../store/toastStore';

const CollegeCard = ({ card, tier, index }) => {
  const [imgError, setImgError] = useState(false);
  const selectedComparison = useChatStore((state) => state.selectedComparison);
  const addComparison = useChatStore((state) => state.addComparison);
  const removeComparison = useChatStore((state) => state.removeComparison);
  const [isSaved, setIsSaved] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const { success, error } = useToastStore();

  if (typeof card === 'string') return <div className="legacy-card">{card}</div>;

  const isSelected = selectedComparison.some(c => c.college_code === card.college_code);
  const handleCompareToggle = () => {
    if (isSelected) {
      removeComparison(card.college_code);
    } else {
      addComparison(card);
    }
  };

  const cfg = TIER_CONFIG[tier] || TIER_CONFIG.SAFE;
  const branches = card.predicted_branches?.length
    ? card.predicted_branches
    : card.available_branches?.slice(0, 6) || [];

  // Show at most N recruiters before "+X more"
  const MAX_RECRUITERS = 4;
  const recruiters = card.top_recruiters || [];

  const handleSaveCollege = async () => {
    if (isSaving || isSaved) return;
    setIsSaving(true);
    try {
      await apiService.post('/api/v1/profile/colleges', {
        college_code: card.college_code,
        branch: branches[0] || 'CSE',
      });
      setIsSaved(true);
      success('College saved successfully');
    } catch (err) {
      console.error(err);
      error('Failed to save college');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className={`cc-card cc-${tier.toLowerCase()}`}>
      {/* ── Numbered Image Block ── */}
      <div className="cc-image-block">
        <div className="cc-number">{index + 1}</div>
        {card.college_image_url && !imgError ? (
          <img
            src={card.college_image_url}
            alt={card.college_name}
            className="cc-image"
            onError={() => setImgError(true)}
          />
        ) : (
          <div className="cc-avatar" style={{ background: codeToGradient(card.college_code) }}>
            {(card.college_code || card.college_name || '??').substring(0, 4)}
          </div>
        )}
      </div>

      {/* ── Main Content ── */}
      <div className="cc-body">
        {/* Top row: Name + Badges */}
        <div className="cc-top">
          <div className="cc-name-block">
            <div className="cc-stars-tier">
              <span className="cc-stars">{cfg.stars}</span>
              <span className="cc-tier-dot" style={{ background: cfg.dot }} />
              <span className="cc-tier-text" style={{ color: cfg.dot }}>{cfg.label}</span>
            </div>
            <h3 className="cc-name">{card.college_name || 'Unknown College'}</h3>
            <div className="cc-location">
              <MapPin size={12} />
              <span>{card.location || 'Telangana'}</span>
            </div>
            
            <div className="cc-compare-toggle">
              <label>
                <input 
                  type="checkbox" 
                  checked={isSelected} 
                  onChange={handleCompareToggle} 
                  disabled={!isSelected && selectedComparison.length >= 3}
                />
                <span className="cc-compare-label">Compare</span>
              </label>
            </div>
            
            <button 
              className="cc-save-btn" 
              onClick={handleSaveCollege} 
              disabled={isSaving || isSaved}
              style={{
                marginLeft: '12px', background: 'none', border: '1px solid #d1d5db',
                padding: '4px 8px', borderRadius: '4px', cursor: 'pointer',
                display: 'inline-flex', alignItems: 'center', gap: '4px',
                fontSize: '0.8rem', color: isSaved ? '#10b981' : '#4b5563',
                fontWeight: 500
              }}
            >
              {isSaved ? <BookmarkCheck size={14} /> : <Bookmark size={14} />}
              {isSaved ? 'Saved' : (isSaving ? 'Saving...' : 'Save')}
            </button>
          </div>
          <div className="cc-badges">
            {card.autonomous && <span className="cc-badge autonomous">AUTONOMOUS</span>}
            {card.affiliated_to && (
              <span className="cc-badge affiliated">AFFILIATED TO {card.affiliated_to}</span>
            )}
          </div>
        </div>

        {/* Quick facts row */}
        <div className="cc-facts-row">
          <div className="cc-fact">
            <span className="cc-fact-label">NAAC GRADE</span>
            <span className="cc-fact-val">{card.naac_grade || 'N/A'}</span>
          </div>
          <div className="cc-fact">
            <span className="cc-fact-label">ESTD.</span>
            <span className="cc-fact-val">{card.established || 'N/A'}</span>
          </div>
          <div className="cc-fact">
            <span className="cc-fact-label">TYPE</span>
            <span className="cc-fact-val">{card.college_type || 'Private'}</span>
          </div>
          {card.nirf_rank && (
            <div className="cc-fact">
              <span className="cc-fact-label">NIRF</span>
              <span className="cc-fact-val">#{card.nirf_rank}</span>
            </div>
          )}
        </div>

        {/* Branches row */}
        <div className="cc-branches-row">
          <span className="cc-branches-label">Popular Branches</span>
          <div className="cc-branches">
            {branches.slice(0, 7).map((b, i) => (
              <span key={i} className="cc-branch-chip">{b}</span>
            ))}
            {branches.length > 7 && (
              <span className="cc-branch-chip more">+{branches.length - 7} more</span>
            )}
          </div>
        </div>

        {/* Footer: website + college code */}
        <div className="cc-footer">
          {card.official_website ? (
            <a
              href={card.official_website}
              target="_blank"
              rel="noopener noreferrer"
              className="cc-website"
            >
              <Globe size={12} />
              Official Website: {card.official_website}
            </a>
          ) : (
            <span className="cc-website-na">No official website listed</span>
          )}
          <div className="cc-code-block">
            <span className="cc-code-label">College Code:</span>
            <span className="cc-code-val">{card.college_code || 'N/A'}</span>
            {card.college_code && <CopyButton text={card.college_code} />}
          </div>
        </div>
      </div>

      {/* ── Stats Panel (right) ── */}
      <div className="cc-stats">
        <div className="cc-stat placement">
          <div className="cc-stat-icon">📈</div>
          <div>
            <div className="cc-stat-label">Last Year Placement</div>
            <div className="cc-stat-val placement-pct">
              {card.placement_percentage ? `${card.placement_percentage}%` : 'N/A'}
            </div>
          </div>
        </div>
        <div className="cc-stat avgpkg">
          <div className="cc-stat-icon">₹</div>
          <div>
            <div className="cc-stat-label">Average Package</div>
            <div className="cc-stat-val avg">{formatLPA(card.avg_package_lpa)}</div>
          </div>
        </div>
        <div className="cc-stat highpkg">
          <div className="cc-stat-icon">🏆</div>
          <div>
            <div className="cc-stat-label">Highest Package</div>
            <div className="cc-stat-val high">{formatLPA(card.highest_package_lpa)}</div>
          </div>
        </div>
        <div className="cc-stat medpkg">
          <div className="cc-stat-icon">⏱</div>
          <div>
            <div className="cc-stat-label">Median Package</div>
            <div className="cc-stat-val med">{formatLPA(card.median_package_lpa)}</div>
          </div>
        </div>

        {/* Recruiters */}
        {recruiters.length > 0 && (
          <div className="cc-recruiters">
            {recruiters.slice(0, MAX_RECRUITERS).map((r, i) => (
              <span key={i} className="cc-recruiter-chip">{r}</span>
            ))}
            {recruiters.length > MAX_RECRUITERS && (
              <span className="cc-recruiter-chip more">+{recruiters.length - MAX_RECRUITERS}</span>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

const TierSection = ({ title, icon, color, cards, tier, isOpen: defaultOpen }) => {
  const [open, setOpen] = useState(defaultOpen);
  if (!cards?.length) return null;
  return (
    <div className="cc-tier-section">
      <button
        className="cc-tier-header"
        style={{ '--tier-c': color }}
        onClick={() => setOpen(o => !o)}
      >
        <span className="cc-tier-icon">{icon}</span>
        <span className="cc-tier-title">{title}</span>
        <span className="cc-tier-count">{cards.length} colleges</span>
        <span className="cc-tier-chevron">{open ? '▲' : '▼'}</span>
      </button>
      {open && (
        <div className="cc-tier-body">
          {cards.map((card, i) => (
            <CollegeCard key={i} card={card} tier={tier} index={i} />
          ))}
        </div>
      )}
    </div>
  );
};

export default function CollegeResponse({ data }) {
  if (!data) return null;
  return (
    <div className="cc-root">
      {/* Header */}
      <div className="cc-header">
        <div className="cc-header-title">
          Predict college for rank {data.rank?.toLocaleString()}, category {data.category}
        </div>
        <div className="cc-header-sub">Here are the best college predictions for your rank.</div>
      </div>

      {/* Profile strip */}
      <div className="cc-profile-strip">
        <div className="cc-profile-pill">🏅 Rank: {data.rank?.toLocaleString() || 'N/A'}</div>
        <div className="cc-profile-pill">👤 Category: {data.category || 'N/A'} ({data.gender || 'N/A'})</div>
        <div className="cc-profile-pill">🎓 Exam: {data.exam || 'EAMCET 2025'}</div>
        <div className="cc-profile-pill">📈 Based on 2024 cutoff trends</div>
      </div>

      {/* Tiers */}
      <div className="cc-tiers">
        <TierSection title="Safe Choices"     icon="🟢" color="#10b981" cards={data.safe}     tier="SAFE"     isOpen={true}  />
        <TierSection title="Moderate Choices" icon="🟡" color="#f59e0b" cards={data.moderate} tier="MODERATE" isOpen={false} />
        <TierSection title="Dream Choices"    icon="🔴" color="#ef4444" cards={data.dream}    tier="DREAM"    isOpen={false} />
      </div>

      <div className="cc-disclaimer">
        ℹ️ Cutoff ranks may vary slightly each year. Please verify with official counselling portal.
      </div>
    </div>
  );
}
