import React, { useState } from 'react';
import { 
  GraduationCap, 
  MapPin, 
  Building2, 
  Award, 
  Briefcase, 
  Globe, 
  Map, 
  ChevronDown, 
  ChevronRight, 
  Star,
  CheckCircle2,
  TrendingUp,
  Scale,
  Sparkles,
  Users
} from 'lucide-react';
import './CollegeResponse.css';

const formatLPA = (val) => val ? `₹${val} LPA` : "N/A";
const formatPct = (val) => val ? `${val}%` : "N/A";

// Progress bar component for Ranks
const RankProgressBar = ({ userRank, closingRank }) => {
  // If userRank is 12000 and closing is 16000, user is 4000 safer.
  // We'll calculate a percentage to fill.
  // 100% full means user is very safe. 
  // Let's make the scale so that if userRank == closingRank, it's 50%.
  // If userRank is 0, it's 100%. If userRank > closingRank (not safe), < 50%.
  if (!userRank || !closingRank) return <span className="fallback-value">N/A</span>;
  
  let pct = 50;
  if (userRank < closingRank) {
    pct = 50 + ((closingRank - userRank) / closingRank) * 50;
  } else {
    pct = (closingRank / userRank) * 50;
  }
  
  // clamp between 5 and 100
  pct = Math.max(5, Math.min(100, pct));
  
  return (
    <div className="progress-bar-container">
      <div className="progress-bar-labels">
        <span className="user-rank">You: {userRank.toLocaleString()}</span>
        <span className="closing-rank">Cutoff: {closingRank.toLocaleString()}</span>
      </div>
      <div className="progress-track">
        <div className="progress-fill rank-fill" style={{ width: `${pct}%` }}></div>
      </div>
    </div>
  );
};

// Progress bar component for Percentages
const PctProgressBar = ({ value }) => {
  if (!value) return <span className="fallback-value">N/A</span>;
  const numValue = typeof value === 'string' ? parseFloat(value) : value;
  const pct = Math.max(0, Math.min(100, numValue));
  
  return (
    <div className="progress-bar-container pct-container">
      <div className="progress-track">
        <div className="progress-fill pct-fill" style={{ width: `${pct}%` }}></div>
      </div>
      <span className="pct-label">{pct}%</span>
    </div>
  );
};

const CollegeCard = ({ card, tier, isBestMatch, userRank }) => {
  const [imgError, setImgError] = useState(false);
  
  if (typeof card === 'string') {
    // Legacy string fallback
    return <div className="legacy-card">{card}</div>;
  }

  // Tier colors
  const tierColors = {
    SAFE: { bg: '#10b98120', text: '#10b981', label: '🟢 SAFE' },
    MODERATE: { bg: '#f59e0b20', text: '#f59e0b', label: '🟡 MODERATE' },
    DREAM: { bg: '#ef444420', text: '#ef4444', label: '🔴 DREAM' }
  };
  
  const tColor = tierColors[tier] || tierColors.SAFE;
  
  const getMatchScore = () => {
    if (tier === 'SAFE') return { stars: 5, text: '★★★★★ Highly Recommended', pct: 92 };
    if (tier === 'MODERATE') return { stars: 4, text: '★★★★☆ Good Match', pct: 75 };
    return { stars: 3, text: '★★★☆☆ Reach School', pct: 45 };
  };
  const match = getMatchScore();

  const getInitials = (name) => {
    if (!name) return "UN";
    return name.split(' ').map(n => n[0]).join('').substring(0, 3).toUpperCase();
  };
  
  const stringToColor = (str) => {
    let hash = 0;
    for (let i = 0; i < str.length; i++) hash = str.charCodeAt(i) + ((hash << 5) - hash);
    return `hsl(${hash % 360}, 70%, 50%)`;
  };

  return (
    <div className="college-card">
      {(card.is_best_match || card.medal_badge) && (
        <div className="best-match-ribbon">
          <Star size={14} fill="currentColor" /> {card.medal_badge || "BEST MATCH"}
        </div>
      )}
      
      <div className="card-header">
        <div className="card-image-container">
          {card.college_image_url && !imgError ? (
            <img 
              src={card.college_image_url} 
              alt={card.college_name} 
              className="college-image" 
              onError={() => setImgError(true)}
            />
          ) : (
            <div className="avatar-fallback" style={{ background: `linear-gradient(135deg, ${stringToColor(card.college_code || card.college_name)}, #2a2a35)` }}>
              {getInitials(card.college_code || card.college_name)}
            </div>
          )}
        </div>
        
        <div className="card-title-area">
          <div className="card-badges-top">
            <span className="match-score">{match.text}</span>
            <span className="tier-badge" style={{ backgroundColor: tColor.bg, color: tColor.text }}>
              {tColor.label}
            </span>
          </div>
          <h3 className="college-name">{card.college_name || "Unknown College"} {card.college_code && `(${card.college_code})`}</h3>
          <div className="location-row">
            <MapPin size={14} /> {card.location || "N/A"}
            {card.autonomous && <span className="pill-badge auto">Autonomous</span>}
            {card.affiliated_to && <span className="pill-badge affil">Affiliated: {card.affiliated_to}</span>}
          </div>
        </div>
      </div>
      
      {/* Main Dashboard Grid */}
      <div className="card-dashboard-grid">
        
        {/* Column 1: Academics & Admission */}
        <div className="grid-col">
          <div className="compact-facts">
            <div className="fact-inline"><span className="label">Established</span> <span className="val">{card.established || "N/A"}</span></div>
            <div className="fact-inline"><span className="label">NAAC</span> <span className="val">{card.naac_grade || "N/A"}</span></div>
            <div className="fact-inline"><span className="label">NIRF</span> <span className="val">{card.nirf_rank || "N/A"}</span></div>
            <div className="fact-inline"><span className="label">NBA</span> <span className="val">{card.nba_accredited ? "Yes" : "No"}</span></div>
          </div>
          
          <div className="admission-compact">
            <div className="fact-inline mt-1">
              <span className="label">Match</span> 
              <span className="val highlight-val">{match.pct}%</span>
            </div>
            <RankProgressBar userRank={userRank} closingRank={card.closing_rank} />
            <div className="cutoff-text">Cutoff: {card.closing_rank?.toLocaleString() || 'N/A'}</div>
          </div>
        </div>

        {/* Column 2: Placements & Recruiters */}
        <div className="grid-col">
          <div className="compact-facts">
            <div className="fact-inline">
              <span className="label">Placement</span> 
              <span className="val bar-wrapper"><PctProgressBar value={card.placement_percentage} /></span>
            </div>
            <div className="fact-inline"><span className="label">Avg Pkg</span> <span className="val highlight-val">{formatLPA(card.avg_package_lpa)}</span></div>
            <div className="fact-inline"><span className="label">Highest</span> <span className="val">{formatLPA(card.highest_package_lpa)}</span></div>
            <div className="fact-inline mt-1"><span className="label">Top Recruiters</span></div>
          </div>
          <div className="chips-container tight">
            {card.top_recruiters && card.top_recruiters.length > 0 ? (
              card.top_recruiters.slice(0, 4).map((r, i) => <span key={i} className="chip outline">{r}</span>)
            ) : (
              <span className="fallback-value">N/A</span>
            )}
          </div>
        </div>

        {/* Column 3: Branches & Facilities */}
        <div className="grid-col">
          <div className="compact-facts">
            <div className="fact-inline"><span className="label">Tuition Fee</span> <span className="val">{card.tuition_fee_per_year ? `₹${card.tuition_fee_per_year.toLocaleString()}/yr` : "N/A"}</span></div>
            <div className="fact-inline"><span className="label">Type</span> <span className="val">{card.college_type || "Private"}</span></div>
            <div className="fact-inline"><span className="label">Hostel</span> <span className="val">{card.hostel_available ? "Yes" : "No"}</span></div>
            <div className="fact-inline mt-1"><span className="label">Predicted Branches</span></div>
          </div>
          <div className="chips-container tight">
            {card.predicted_branches && card.predicted_branches.length > 0 ? (
              card.predicted_branches.map((b, i) => <span key={i} className="chip primary">{b}</span>)
            ) : (
              <span className="fallback-value">No specific branches predicted</span>
            )}
          </div>
        </div>

      </div>

      {/* Action Footer (AI + Buttons) */}
      <div className="card-footer-compact">
        <div className="ai-rec-text" style={{ flexDirection: 'column', alignItems: 'flex-start', gap: '8px' }}>
          {card.reason_for_recommendation && (
            <div style={{ display: 'flex', gap: '6px', alignItems: 'flex-start' }}>
              <Sparkles size={12} className="text-accent flex-shrink-0" style={{ marginTop: '2px' }} />
              <span className="ai-text" title={card.reason_for_recommendation}>{card.reason_for_recommendation}</span>
            </div>
          )}
          {card.parent_summary && (
            <div style={{ display: 'flex', gap: '6px', alignItems: 'flex-start' }}>
              <Users size={12} className="text-accent flex-shrink-0" style={{ marginTop: '2px' }} />
              <span className="ai-text" style={{ fontStyle: 'italic', color: 'var(--text-primary)' }} title={card.parent_summary}>
                <strong>Parent Summary:</strong> {card.parent_summary}
              </span>
            </div>
          )}
        </div>

        <div className="action-links-compact">
          {card.official_website && (
            <a href={card.official_website} target="_blank" rel="noopener noreferrer" className="btn-action primary compact">
              <Globe size={12} /> <span className="btn-label">Site</span>
            </a>
          )}
          {card.google_maps_url && (
            <a href={card.google_maps_url} target="_blank" rel="noopener noreferrer" className="btn-action secondary compact">
              <Map size={12} /> <span className="btn-label">Map</span>
            </a>
          )}
          <button className="btn-action outline compact compare-btn">
            <Scale size={12} /> <span className="btn-label">Compare</span>
          </button>
        </div>
      </div>

    </div>
  );
};

const CollegeTierSection = ({ title, cards, tier, icon, color, userRank, isOpenDefault = false }) => {
  const [isOpen, setIsOpen] = useState(isOpenDefault);

  if (!cards || cards.length === 0) return null;

  return (
    <div className="tier-section">
      <button 
        className="tier-header" 
        onClick={() => setIsOpen(!isOpen)}
        style={{ '--tier-color': color }}
      >
        <div className="tier-title-left">
          <span className="tier-icon">{icon}</span>
          <h2>{title} ({cards.length})</h2>
        </div>
        <div className="tier-toggle">
          {isOpen ? <ChevronDown size={20} /> : <ChevronRight size={20} />}
        </div>
      </button>

      {isOpen && (
        <div className="tier-cards-container">
          {cards.map((card, idx) => (
            <CollegeCard 
              key={idx} 
              card={card} 
              tier={tier} 
              isBestMatch={tier === 'SAFE' && idx === 0} 
              userRank={userRank}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default function CollegeResponse({ data }) {
  if (!data) return null;

  const userRank = data.rank;

  return (
    <div className="structured-response college-response-v2">
      <div className="response-title college-hero">
        <GraduationCap size={24} className="hero-icon" />
        <div className="hero-text">
          <h1>College Predictor Results</h1>
          <p>Based on your EAMCET 2025 profile</p>
        </div>
      </div>

      <div className="student-profile-bar">
        <div className="profile-item"><span>Rank:</span> <strong>{userRank?.toLocaleString() || "N/A"}</strong></div>
        <div className="profile-item"><span>Category:</span> <strong>{data.category || "N/A"}</strong></div>
        <div className="profile-item"><span>Gender:</span> <strong>{data.gender || "N/A"}</strong></div>
        <div className="profile-item"><span>Branch:</span> <strong>{data.branch || "Any"}</strong></div>
        <div className="profile-item"><span>Location:</span> <strong>{data.location || "Any"}</strong></div>
      </div>

      <div className="tiers-container">
        <CollegeTierSection 
          title="Safe Choices" 
          cards={data.safe} 
          tier="SAFE" 
          icon="🟢" 
          color="#10b981" 
          userRank={userRank}
          isOpenDefault={true} 
        />
        <CollegeTierSection 
          title="Moderate Choices" 
          cards={data.moderate} 
          tier="MODERATE" 
          icon="🟡" 
          color="#f59e0b"
          userRank={userRank} 
          isOpenDefault={false} 
        />
        <CollegeTierSection 
          title="Dream Choices" 
          cards={data.dream} 
          tier="DREAM" 
          icon="🔴" 
          color="#ef4444" 
          userRank={userRank}
          isOpenDefault={false} 
        />
      </div>
      
      <div className="disclaimer-footer">
        <p>ℹ️ Based on previous year EAMCET cutoffs. Actual allotment may vary.</p>
      </div>
    </div>
  );
}
