import React from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';

const AuditCampaign: React.FC = () => {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const isRtl = i18n.language === 'ar';

  return (
    <div className="min-h-screen bg-tech-black" dir={isRtl ? 'rtl' : 'ltr'}>
      {/* NAV */}
      <nav className="border-b border-white/5 px-6 h-16 flex items-center">
        <div className="max-w-6xl mx-auto w-full flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-full bg-primary/20 border border-primary/40 flex items-center justify-center">
              <span className="text-primary font-bold text-xs">و</span>
            </div>
            <span className="text-white font-semibold">Wathiq</span>
          </div>
          <a href="https://wathiq-delta.vercel.app/login" className="text-white-grey hover:text-white text-sm transition">Sign in</a>
        </div>
      </nav>

      {/* HERO */}
      <section className="relative overflow-hidden pt-20 pb-16">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[600px] bg-red-500/5 rounded-full blur-3xl"></div>
        <div className="max-w-4xl mx-auto px-6 text-center relative z-10">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-red-500/10 border border-red-500/20 rounded-full text-red-400 text-xs font-medium mb-5">
            <span className="w-1.5 h-1.5 bg-red-400 rounded-full animate-pulse"></span>
            Deadline: June 30, 2026 — 23 Days Left
          </div>
          <h1 className="text-4xl md:text-6xl font-onest text-white leading-tight mb-5">
            Your Qiwa Balance <span className="text-red-400">Disappeared?</span>
          </h1>
          <p className="text-lg text-charcoal max-w-3xl mx-auto mb-8 leading-relaxed">
            We'll scan your workforce for <strong className="text-white">free</strong> and show you 
            exactly which contracts are undocumented, which employees are heading for the 90-day 
            runaway flag, and how to fix it before June 30.
          </p>
          <button
            onClick={() => navigate('/qiwa-shield')}
            className="bg-primary hover:bg-primary-dark text-tech-black font-semibold text-base px-10 py-4 rounded-xl transition shadow-lg shadow-primary/20 inline-block"
          >
            Start Free Audit →
          </button>
          <p className="text-xs text-charcoal mt-3">No credit card. No signup. Takes 2 minutes.</p>
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section className="border-t border-white/5 py-16">
        <div className="max-w-6xl mx-auto px-6">
          <h2 className="text-2xl md:text-3xl text-white font-onest text-center mb-10">How It Works</h2>
          <div className="grid md:grid-cols-3 gap-6">
            {[
              { num: '1', title: 'Upload Your Payroll', desc: 'Export your employee list as CSV or Excel. Drag and drop it onto our secure scanner.' },
              { num: '2', title: 'AI Scans Everything', desc: 'Our engine checks every Saudi employee against Qiwa rules, Nitaqat, GOSI, and the 90-day runaway flag.' },
              { num: '3', title: 'Get Your Rescue Plan', desc: 'Download a prioritized action plan showing which contracts need documenting and your penalty savings.' },
            ].map((step) => (
              <div key={step.num} className="text-center p-6">
                <div className="w-12 h-12 mx-auto mb-4 rounded-xl bg-primary/10 flex items-center justify-center text-xl font-bold text-primary">{step.num}</div>
                <h3 className="text-lg text-white font-onest mb-2">{step.title}</h3>
                <p className="text-sm text-charcoal leading-relaxed">{step.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* URGENCY */}
      <section className="border-t border-white/5 py-16">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <div className="bg-red-500/5 border border-red-500/20 rounded-2xl p-10">
            <h2 className="text-2xl md:text-3xl text-white font-onest mb-5">23 Days to June 30</h2>
            <p className="text-charcoal mb-6 max-w-xl mx-auto text-sm leading-relaxed">
              After June 30, undocumented Saudi employees count as <strong className="text-white">zero</strong> for Saudization. 
              One undocumented employee can drop your Nitaqat band — meaning <strong className="text-red-400">no visas, no renewals</strong>.
            </p>
            <button
              onClick={() => navigate('/qiwa-shield')}
              className="bg-primary hover:bg-primary-dark text-tech-black font-semibold text-sm px-8 py-3.5 rounded-xl transition"
            >
              Start Free Audit — 2 Minutes
            </button>
          </div>
        </div>
      </section>

      <footer className="border-t border-white/5 py-8">
        <div className="max-w-6xl mx-auto px-6 text-center">
          <p className="text-xs text-charcoal">©2026 Wathiq. Compliance infrastructure for Saudi Arabia.</p>
        </div>
      </footer>
    </div>
  );
};

export default AuditCampaign;