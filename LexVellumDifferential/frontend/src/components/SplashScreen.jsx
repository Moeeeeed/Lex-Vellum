import React, { useEffect, useState } from 'react';

export default function SplashScreen({ onFinish }) {
  const [phase, setPhase] = useState('logo'); // 'logo' -> 'text' -> 'fade'

  useEffect(() => {
    const timer1 = setTimeout(() => setPhase('text'), 1500);
    const timer2 = setTimeout(() => setPhase('fade'), 3500);
    const timer3 = setTimeout(() => onFinish(), 4000);
    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
    };
  }, [onFinish]);

  return (
    <div className={`splash-screen ${phase === 'fade' ? 'fade-out' : ''}`}>
      <div className="splash-content">
        <div className={`splash-art ${phase === 'logo' || phase === 'text' ? 'visible' : ''}`}>
          {/* Simple SVG Line Art of a Gavel (Replacement for provided images) */}
          <svg width="200" height="200" viewBox="0 0 100 100" fill="none" stroke="currentColor" strokeWidth="1.5">
             <path d="M30 70 L70 70" strokeLinecap="round" />
             <path d="M40 70 L40 60 L60 60 L60 70" />
             <path d="M45 60 L45 50 L55 50 L55 60" />
             <rect x="35" y="35" width="30" height="15" rx="2" transform="rotate(-30 50 42.5)" />
             <path d="M60 38 L85 25" strokeLinecap="round" />
          </svg>
        </div>
        <div className={`splash-text ${phase === 'text' ? 'visible' : ''}`}>
          {"LEXVELLUM".split("").map((char, i) => (
            <span key={i} style={{ animationDelay: `${i * 0.1}s` }}>{char}</span>
          ))}
        </div>
      </div>
    </div>
  );
}
