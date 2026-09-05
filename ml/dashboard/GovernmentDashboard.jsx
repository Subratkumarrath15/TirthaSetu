/**
 * TirthaSetu Government Command & Control Dashboard (React Component)
 *
 * Complete unified government portal featuring:
 * - Real-time polling (every 3s)
 * - Dynamic risk badges & master safety gauge
 * - AI forecast & stateful complex census
 * - Active Incident Command Center with Acknowledge/Resolve actions
 * - Analytics & Decision Insights (Executive KPIs, Trends, Risk Distribution, Temple Matrix)
 * - 4-Zone telemetry feeds
 * - Interactive Hackathon Demo Scenario progression switcher
 */

import React, { useState, useEffect } from 'react';

const API_BASE = "http://127.0.0.1:8000";

export default function GovernmentDashboard() {
  const [temple, setTemple] = useState("Somnath");
  const [activeScenario, setActiveScenario] = useState(null);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);
  const [incidents, setIncidents] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [templeComp, setTempleComp] = useState([]);
  const [error, setError] = useState(null);

  const fetchStatus = async () => {
    setLoading(true);
    try {
      let url;
      if (activeScenario) {
        url = `${API_BASE}/api/demo/${activeScenario}`;
      } else {
        const params = new URLSearchParams({
          hour: "10",
          day_of_week: "Thursday",
          is_weekend: "0",
          is_holiday: "0",
          is_festival: "0",
          weather: "Sunny",
          temperature: "30",
          previous_visitors: "4500"
        });
        url = `${API_BASE}/api/full-status/${encodeURIComponent(temple)}?${params.toString()}`;
      }

      const res = await fetch(url);
      if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`);
      const json = await res.json();
      setData(json);
      setError(null);
      fetchIncidents();
      fetchAnalyticsData();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchIncidents = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/incidents/active`);
      if (res.ok) {
        const json = await res.json();
        setIncidents(json.incidents || []);
      }
    } catch (err) {
      console.error("Error fetching incidents:", err);
    }
  };

  const fetchAnalyticsData = async () => {
    try {
      const [sumRes, compRes] = await Promise.all([
        fetch(`${API_BASE}/api/analytics/summary`),
        fetch(`${API_BASE}/api/analytics/temple-comparison`)
      ]);
      if (sumRes.ok) {
        const sJson = await sumRes.json();
        setAnalytics(sJson.summary);
      }
      if (compRes.ok) {
        const cJson = await compRes.json();
        setTempleComp(cJson.comparison || []);
      }
    } catch (err) {
      console.error("Error fetching analytics:", err);
    }
  };

  const handleAcknowledge = async (id) => {
    try {
      await fetch(`${API_BASE}/api/incidents/${id}/acknowledge`, { method: 'POST' });
      fetchIncidents();
      fetchAnalyticsData();
    } catch (err) {
      console.error("Error acknowledging incident:", err);
    }
  };

  const handleResolve = async (id) => {
    try {
      await fetch(`${API_BASE}/api/incidents/${id}/resolve`, { method: 'POST' });
      fetchIncidents();
      fetchAnalyticsData();
    } catch (err) {
      console.error("Error resolving incident:", err);
    }
  };

  const handleScenarioChange = (slug, tName) => {
    setActiveScenario(slug);
    setTemple(tName);
  };

  useEffect(() => {
    fetchStatus();
    let timer = null;
    if (autoRefresh) {
      timer = setInterval(() => {
        fetchStatus();
      }, 3000);
    }
    return () => { if (timer) clearInterval(timer); };
  }, [temple, activeScenario, autoRefresh]);

  const getRiskStyles = (level) => {
    switch (level) {
      case 'CRITICAL':
        return { badge: 'bg-red-500/20 text-red-400 border-red-500/40', bar: 'bg-red-500', text: 'text-red-400' };
      case 'HIGH':
        return { badge: 'bg-orange-500/20 text-orange-400 border-orange-500/40', bar: 'bg-orange-500', text: 'text-orange-300' };
      case 'MODERATE':
        return { badge: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/40', bar: 'bg-yellow-500', text: 'text-yellow-300' };
      default:
        return { badge: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40', bar: 'bg-emerald-500', text: 'text-emerald-300' };
    }
  };

  const intel = data?.intelligence || {};
  const ai = intel.ai_prediction || {};
  const live = intel.live_data || {};
  const crowd = intel.crowd_intelligence || {};
  const resources = data?.resource_recommendations || {};
  const risk = crowd.final_risk_level || 'LOW';
  const riskStyles = getRiskStyles(risk);

  return (
    <div className="bg-slate-950 text-slate-100 min-h-screen p-4 sm:p-6 lg:p-8 space-y-6">
      {/* Header */}
      <header className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <h1 className="text-2xl font-black tracking-tight text-white flex items-center gap-2">
            <span>TirthaSetu Gujarat Command Center</span>
            <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-semibold">Live AI Active</span>
          </h1>
          <p className="text-xs text-slate-400">Pilgrim Safety, Incident Command & Operational Resource Dispatch for Gujarat Shrines</p>
        </div>

        <div className="flex items-center gap-3">
          <select
            value={temple}
            onChange={(e) => { setActiveScenario(null); setTemple(e.target.value); }}
            className="bg-slate-900 border border-slate-700 text-white rounded-lg px-3 py-1.5 text-sm font-semibold focus:ring-2 focus:ring-emerald-500"
          >
            <option value="Somnath">Somnath</option>
            <option value="Dwarka">Dwarka</option>
            <option value="Ambaji">Ambaji</option>
            <option value="Pavagadh">Pavagadh</option>
          </select>

          <button
            onClick={fetchStatus}
            disabled={loading}
            className="px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-xs font-bold text-white transition flex items-center gap-1.5 shadow"
          >
            <span>{loading ? "Refreshing..." : "Refresh"}</span>
          </button>
        </div>
      </header>

      {/* Hackathon Demo Banner */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 flex flex-col md:flex-row md:items-center justify-between gap-3">
        <div>
          <span className="text-xs font-bold text-amber-400 uppercase tracking-wider block">Interactive Hackathon Demo Scenarios</span>
          <span className="text-xs text-slate-400">Trigger deterministic situations live during presentations:</span>
        </div>
        <div className="flex flex-wrap gap-2">
          <button onClick={() => handleScenarioChange('normal-day', 'Somnath')} className={`px-2.5 py-1 text-xs font-semibold rounded-lg border ${activeScenario === 'normal-day' ? 'bg-emerald-600 text-white border-emerald-400 ring-2 ring-white' : 'bg-emerald-500/10 text-emerald-300 border-emerald-500/20'}`}>1. Normal Day (LOW)</button>
          <button onClick={() => handleScenarioChange('busy-weekend', 'Dwarka')} className={`px-2.5 py-1 text-xs font-semibold rounded-lg border ${activeScenario === 'busy-weekend' ? 'bg-yellow-600 text-white border-yellow-400 ring-2 ring-white' : 'bg-yellow-500/10 text-yellow-300 border-yellow-500/20'}`}>2. Weekend (MODERATE)</button>
          <button onClick={() => handleScenarioChange('festival-rush', 'Ambaji')} className={`px-2.5 py-1 text-xs font-semibold rounded-lg border ${activeScenario === 'festival-rush' ? 'bg-orange-600 text-white border-orange-400 ring-2 ring-white' : 'bg-orange-500/10 text-orange-300 border-orange-500/20'}`}>3. Festival (HIGH)</button>
          <button onClick={() => handleScenarioChange('emergency-overcrowding', 'Pavagadh')} className={`px-2.5 py-1 text-xs font-semibold rounded-lg border ${activeScenario === 'emergency-overcrowding' ? 'bg-red-600 text-white border-red-400 ring-2 ring-white' : 'bg-red-500/10 text-red-300 border-red-500/20'}`}>4. Emergency (CRITICAL)</button>
          <button onClick={() => setActiveScenario(null)} className={`px-2.5 py-1 text-xs font-semibold rounded-lg border ${!activeScenario ? 'bg-slate-700 text-white border-slate-500 ring-2 ring-emerald-400' : 'bg-slate-800 text-slate-300 border-slate-700'}`}>Live Sensor Feed</button>
        </div>
      </div>

      {error && (
        <div className="bg-rose-500/20 border border-rose-500/40 text-rose-300 p-3 rounded-xl text-xs">
          Error connecting to AI API: {error}
        </div>
      )}

      {/* Main KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Unified Crowd Score */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-lg space-y-3">
          <div className="flex justify-between items-center text-xs text-slate-400 uppercase font-bold">
            <span>Unified Safety Score</span>
            <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-200 border border-slate-700">{crowd.trend || 'STABLE'}</span>
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-4xl font-extrabold text-white">{(crowd.final_crowd_score || 0).toFixed(1)}%</span>
            <span className={`px-3 py-1 rounded-xl text-xs font-black uppercase border ${riskStyles.badge}`}>{risk}</span>
          </div>
          <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
            <div className={`h-2 rounded-full transition-all duration-500 ${riskStyles.bar}`} style={{ width: `${Math.min(100, crowd.final_crowd_score || 0)}%` }}></div>
          </div>
        </div>

        {/* AI Forecast */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-lg space-y-3">
          <div className="flex justify-between items-center text-xs text-slate-400 uppercase font-bold">
            <span>AI Predictive Inflow</span>
            <span className="text-emerald-400">ML Forecast</span>
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-3xl font-extrabold text-white">{(ai.predicted_visitors || 0).toLocaleString()}</span>
            <span className="text-xs font-semibold text-slate-400">Capacity: {(ai.crowd_percentage || 0).toFixed(1)}%</span>
          </div>
          <p className="text-xs text-slate-400">Next hour projected arrivals based on weather, darshan schedule & festival flags.</p>
        </div>

        {/* Live Census */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-lg space-y-3">
          <div className="flex justify-between items-center text-xs text-slate-400 uppercase font-bold">
            <span>Live Complex Census</span>
            <span className="text-sky-400">IoT Telemetry</span>
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-3xl font-extrabold text-white">{(live.total_current_people || 0).toLocaleString()}</span>
            <span className="text-xs font-semibold text-slate-400">Avg Density: {(live.average_density || 0).toFixed(1)}%</span>
          </div>
          <p className="text-xs text-slate-400">Parking Occupancy: <strong>{(live.parking_occupancy || 0).toFixed(1)}%</strong> | Peak: <strong>{live.highest_risk_zone || '--'}</strong></p>
        </div>
      </div>

      {/* ACTIVE INCIDENT COMMAND CENTER */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
        <div className="flex justify-between items-center border-b border-slate-800 pb-3">
          <div className="flex items-center gap-2">
            <span className="text-lg">🚨</span>
            <h2 className="text-base font-bold text-white">Active Incident Command Center</h2>
          </div>
          <span className={`px-2.5 py-0.5 rounded text-xs font-black uppercase border ${incidents.length > 0 ? 'bg-red-500/20 text-red-400 border-red-500/40 animate-pulse' : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'}`}>
            {incidents.length} Active Incident{incidents.length === 1 ? '' : 's'}
          </span>
        </div>

        {incidents.length === 0 ? (
          <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-xl p-4 text-xs text-emerald-300 flex items-center gap-2">
            <span>✅</span>
            <span>All temple zones operating within safe capacity limits. No active safety incident alerts.</span>
          </div>
        ) : (
          <div className="space-y-3">
            {incidents.map((inc) => {
              const iStyles = getRiskStyles(inc.risk_level);
              const isAck = inc.status === 'ACKNOWLEDGED';
              return (
                <div key={inc.incident_id} className={`border rounded-xl p-4 flex flex-col md:flex-row md:items-center justify-between gap-4 ${inc.risk_level === 'CRITICAL' ? 'border-red-500/40 bg-red-500/10' : 'border-orange-500/40 bg-orange-500/10'}`}>
                  <div className="space-y-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-black uppercase border ${iStyles.badge}`}>{inc.risk_level}</span>
                      <span className="text-xs font-mono font-bold text-slate-400">{inc.incident_id}</span>
                      <span className="text-xs font-bold text-white">• {inc.temple} — <strong className={iStyles.text}>{inc.zone}</strong></span>
                      <span className={`text-xs font-extrabold ${iStyles.text}`}>({inc.density.toFixed(1)}% Saturation)</span>
                      {isAck ? <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-500/20 text-blue-300 border border-blue-500/30">ACKNOWLEDGED</span> : <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-red-500/20 text-red-300 border border-red-500/30">DISPATCH REQUIRED</span>}
                    </div>
                    <p className="text-xs text-slate-200">{inc.message}</p>
                    <div className="text-[11px] text-slate-400">Reported: {inc.created_at} {inc.acknowledged_at ? `| Acknowledged: ${inc.acknowledged_at}` : ''}</div>
                  </div>

                  <div className="flex items-center gap-2 self-end md:self-center">
                    {!isAck ? (
                      <button onClick={() => handleAcknowledge(inc.incident_id)} className="px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-xs font-bold text-white transition">Acknowledge</button>
                    ) : (
                      <button disabled className="px-3 py-1.5 rounded-lg bg-blue-900/40 text-blue-300 text-xs font-bold border border-blue-800/60 cursor-not-allowed">Acknowledged</button>
                    )}
                    <button onClick={() => handleResolve(inc.incident_id)} className="px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-xs font-bold text-white transition">Resolve</button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* ANALYTICS & DECISION INSIGHTS */}
      {analytics && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
          <div className="flex justify-between items-center border-b border-slate-800 pb-3">
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <span>📊</span>
              <span>Analytics & Decision Insights</span>
            </h2>
            <span className="text-xs text-emerald-400 uppercase font-semibold">Continuous Intelligence</span>
          </div>

          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
              <span className="text-xs font-bold text-slate-400 uppercase block">Average Crowd Score</span>
              <div className="text-2xl font-black text-white mt-1">{analytics.average_crowd_score}%</div>
              <span className="text-[11px] text-slate-500">Across rolling history</span>
            </div>
            <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
              <span className="text-xs font-bold text-slate-400 uppercase block">Highest-Risk Shrine</span>
              <div className="text-2xl font-black text-white mt-1">{analytics.highest_risk_temple}</div>
              <span className="text-[11px] text-red-400 font-semibold">Tier: {analytics.highest_risk_level}</span>
            </div>
            <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
              <span className="text-xs font-bold text-slate-400 uppercase block">Active Incidents</span>
              <div className="text-2xl font-black text-amber-400 mt-1">{analytics.incident_summary.active} Active</div>
              <span className="text-[11px] text-slate-500">{analytics.incident_summary.critical} Critical</span>
            </div>
            <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
              <span className="text-xs font-bold text-slate-400 uppercase block">Critical Bottleneck</span>
              <div className="text-2xl font-black text-purple-400 mt-1">{analytics.most_affected_zone}</div>
              <span className="text-[11px] text-slate-500">Most frequent surge zone</span>
            </div>
          </div>

          <div className="bg-slate-950/80 border border-emerald-500/20 p-3.5 rounded-xl text-xs text-slate-200">
            <strong className="text-amber-300 block mb-0.5">Executive Operational Recommendation:</strong>
            <p>{analytics.operational_insight}</p>
          </div>

          {/* Temple Comparative Matrix */}
          <div className="space-y-2">
            <span className="text-xs font-bold text-slate-300 uppercase block">Cross-Shrine Capacity & Risk Comparison</span>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
              {templeComp.map((t, idx) => {
                const tStyles = getRiskStyles(t.risk_level);
                return (
                  <div key={idx} className="bg-slate-950 p-3 rounded-xl border border-slate-800 space-y-1.5">
                    <div className="flex justify-between items-center">
                      <span className="text-xs font-bold text-white">{t.temple}</span>
                      <span className={`px-1.5 py-0.2 rounded text-[9px] font-black uppercase border ${tStyles.badge}`}>{t.risk_level}</span>
                    </div>
                    <div className="text-lg font-black text-white">{t.latest_crowd_score.toFixed(1)}%</div>
                    <div className="w-full bg-slate-800 rounded-full h-1 overflow-hidden">
                      <div className={`h-1 rounded-full ${tStyles.bar}`} style={{ width: `${Math.min(100, t.latest_crowd_score)}%` }}></div>
                    </div>
                    <div className="flex justify-between text-[10px] text-slate-400">
                      <span>Max: {t.max_zone_density.toFixed(0)}%</span>
                      <span className={t.active_incidents > 0 ? 'text-red-400 font-bold' : 'text-slate-500'}>{t.active_incidents} alerts</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* Operational Directives & Resource Allocation */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
        <div className="flex justify-between items-center border-b border-slate-800 pb-3">
          <h2 className="text-base font-bold text-white">Smart Resource Allocation & Response Directives</h2>
          <span className={`px-2.5 py-0.5 rounded text-xs font-black uppercase border ${riskStyles.badge}`}>
            Priority: {data?.emergency_priority || 'LOW'}
          </span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
            <div className="text-2xl font-black text-blue-400">{resources.security_personnel || 0} Units</div>
            <div className="text-xs text-slate-400 mt-1">Security Allocation</div>
          </div>
          <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
            <div className="text-2xl font-black text-rose-400">{resources.medical_personnel || 0} Units</div>
            <div className="text-xs text-slate-400 mt-1">Medical Personnel</div>
          </div>
          <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
            <div className="text-2xl font-black text-amber-400">+{resources.additional_gates || 0} Gates</div>
            <div className="text-xs text-slate-400 mt-1">Additional Gates</div>
          </div>
          <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
            <div className="text-sm font-bold text-white mt-1">{resources.emergency_team_alert ? "🚨 Standby" : "Routine"}</div>
            <div className="text-xs text-slate-400 mt-1">Emergency Team</div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 text-xs">
            <span className="font-bold text-slate-400 uppercase block mb-1">Queue Protocol</span>
            <p className="text-slate-200 text-sm font-medium">{ops.queue_action || "Normal queue operations"}</p>
          </div>
          <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 text-xs">
            <span className="font-bold text-slate-400 uppercase block mb-1">Parking Directive</span>
            <p className="text-slate-200 text-sm font-medium">{ops.parking_action || "Normal parking operations."}</p>
          </div>
        </div>
      </div>

      {/* Multi-Zone Sensor Feeds */}
      <div className="space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div className="flex items-center space-x-3">
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300">
              {activeScenario ? "Scenario Multi-Zone Telemetry" : "Live Multi-Zone Sensor Feeds"}
            </h3>
            <span className={`px-2.5 py-0.5 rounded text-[11px] font-extrabold uppercase border ${
              activeScenario
                ? 'bg-amber-500/15 text-amber-400 border-amber-500/30'
                : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
            }`}>
              {activeScenario ? `DEMO SCENARIO DATA — ${activeScenario.toUpperCase()}` : "LIVE SIMULATOR DATA"}
            </span>
          </div>
          <span className="text-xs text-slate-400">
            {activeScenario ? "Controlled deterministic telemetry" : "Updated every 3 seconds via IoT Simulator"}
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {zones.map((z, idx) => {
            const density = z.crowd_density !== undefined ? z.crowd_density : 0;
            const zStyles = getRiskStyles(z.risk_level || (density >= 85 ? 'CRITICAL' : density >= 70 ? 'HIGH' : density >= 40 ? 'MODERATE' : 'LOW'));
            return (
              <div key={idx} className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-3 shadow-md">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-white">{z.zone}</span>
                  <span className={`px-2 py-0.5 rounded text-[10px] font-extrabold uppercase border ${zStyles.badge}`}>{z.risk_level}</span>
                </div>
                <div className="flex items-baseline justify-between">
                  <span className="text-2xl font-black text-white">{density.toFixed(1)}%</span>
                  <span className="text-xs text-slate-400">{(z.current_people || 0).toLocaleString()} people</span>
                </div>
                <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                  <div className={`h-1.5 rounded-full ${zStyles.bar}`} style={{ width: `${Math.min(100, density)}%` }}></div>
                </div>
                <div className="flex justify-between text-[11px] text-slate-400 pt-1 border-t border-slate-800/60">
                  <span className="text-emerald-400/90 font-medium">In: +{z.people_entering}/min</span>
                  <span className="text-slate-400 font-medium">Out: -{z.people_exiting}/min</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
