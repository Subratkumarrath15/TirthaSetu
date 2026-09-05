import React, { useCallback, useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './styles.css';

const REQUIRED_TEMPLES = [
  'Somnath',
  'Dwarka',
  'Ambaji',
  'Pavagadh'
];

const API_BASE =
  import.meta.env.VITE_API_BASE || 'http://localhost:5000';

/*
  GOOGLE FORM
  QR CODE opens this URL.
*/
const GOOGLE_FORM_URL =
  'https://docs.google.com/forms/d/e/1FAIpQLScJB2PIlts9_1u_rwQDyqY4K8r_dhEVOuYCMtZk_AZO8WCn6w/viewform';


/* =========================
   API HELPER
========================= */

const api = async (path, options = {}) => {
  const r = await fetch(API_BASE + path, options);

  let d = {};

  try {
    d = await r.json();
  } catch {
    d = {};
  }

  if (!r.ok) {
    throw new Error(
      d?.detail ||
      d?.message ||
      `API error ${r.status}`
    );
  }

  return d;
};


/* =========================
   HELPERS
========================= */

const n = v =>
  Number.isFinite(Number(v))
    ? Number(v).toLocaleString()
    : '—';


const tone = r =>
  r === 'LOW'
    ? 'green'
    : r === 'MODERATE'
      ? 'amber'
      : 'red';


const ztone = r =>
  r === 'LOW'
    ? 'low'
    : r === 'MODERATE'
      ? 'med'
      : 'high';


const Btn = ({
  children,
  onClick,
  kind = '',
  disabled
}) =>
  <button
    className={'btn ' + kind}
    onClick={onClick}
    disabled={disabled}
  >
    {children}
  </button>;


const TempleSelect = ({
  value,
  onChange,
  temples = REQUIRED_TEMPLES
}) =>
  <select
    value={value}
    onChange={e => onChange(e.target.value)}
    disabled={!temples.length}
  >
    {temples.length
      ? temples.map(t =>
          <option key={t}>{t}</option>
        )
      : <option>Loading temples…</option>
    }
  </select>;


const Section = ({
  kicker,
  title,
  sub
}) =>
  <div className="section">
    <div className="eyebrow">{kicker}</div>
    <h2>{title}</h2>
    <p>{sub}</p>
  </div>;


const Stat = ({
  title,
  value,
  text,
  tone = ''
}) =>
  <div className="stat">

    <div className={'statIcon ' + tone}>
      ◉
    </div>

    <div>
      <span>{title}</span>
      <strong>{value}</strong>
      <small>{text}</small>
    </div>

  </div>;


/* =========================
   MAIN APP
========================= */

function App() {

  const [mode, setMode] = useState('pilgrim');

  const [temple, setTemple] = useState('Somnath');

  const [temples, setTemples] = useState(
    REQUIRED_TEMPLES
  );

  const [lang, setLang] = useState('EN');

  const [status, setStatus] = useState(null);

  const [incidents, setIncidents] = useState([]);

  const [loading, setLoading] = useState(true);

  const [error, setError] = useState('');

  const [modal, setModal] = useState(null);

  const [toast, setToast] = useState('');


  const notify = useCallback(m => {
    setToast(m);

    clearTimeout(window._ts);

    window._ts = setTimeout(
      () => setToast(''),
      3000
    );
  }, []);


  const refresh = useCallback(async () => {

    setLoading(true);
    setError('');

    try {

      const [s, i] = await Promise.all([

        api(
          `/api/ai/full-status/${encodeURIComponent(temple)}`
        ),

        api(
          `/api/ai/incidents/active?temple=${encodeURIComponent(temple)}`
        )

      ]);

      setStatus(s);
      setIncidents(i.incidents || []);

    }

    catch (e) {

      setError(e.message);
      setStatus(null);
      setIncidents([]);

    }

    finally {

      setLoading(false);

    }

  }, [temple]);


  useEffect(() => {

    let active = true;

    api('/api/ai/temples')

      .then(r => {

        const live = (r.temples || [])
          .filter(t =>
            REQUIRED_TEMPLES.includes(t)
          );

        if (active && live.length)
          setTemples(live);

      })

      .catch(() => {});

    return () => {
      active = false;
    };

  }, []);


  useEffect(() => {

    refresh();

    const id = setInterval(
      refresh,
      15000
    );

    return () => {
      clearInterval(id);
    };

  }, [refresh]);


  return (

    <div>

      <Header
        mode={mode}
        setMode={setMode}
        temple={temple}
        temples={temples}
        setTemple={setTemple}
        setLang={setLang}
      />


      {error &&

        <div className="wrap">

          <div className="notice">

            <b>
              Live service unavailable
            </b>

            <p>{error}</p>

            <Btn
              kind="soft"
              onClick={refresh}
            >
              Retry
            </Btn>

          </div>

        </div>

      }


      {mode === 'pilgrim'

        ?

        <Pilgrim
          temple={temple}
          temples={temples}
          setTemple={setTemple}
          status={status}
          loading={loading}
          open={setModal}
          notify={notify}
        />

        :

        <Admin
          temple={temple}
          temples={temples}
          setTemple={setTemple}
          status={status}
          incidents={incidents}
          loading={loading}
          refresh={refresh}
          notify={notify}
        />

      }


      {modal === 'book' &&

        <Booking
          temple={temple}
          status={status}
          close={() => setModal(null)}
          notify={notify}
        />

      }


      {modal === 'sos' &&

        <SOS
          temple={temple}
          close={() => setModal(null)}
          notify={notify}
        />

      }


      {modal === 'assist' &&

        <Assist
          temple={temple}
          close={() => setModal(null)}
          notify={notify}
        />

      }


      {modal === 'lang' &&

        <Lang
          value={lang}
          set={setLang}
          close={() => setModal(null)}
        />

      }


      {modal === 'guidance' &&

        <Guidance
          temple={temple}
          status={status}
          close={() => setModal(null)}
        />

      }


      {toast &&

        <div className="toast">
          ✓ <span>{toast}</span>
        </div>

      }

    </div>

  );

}


/* =========================
   HEADER
========================= */

function Header({
  mode,
  setMode,
  temple,
  temples,
  setTemple,
  setLang
}) {

  return (

    <header>

      <div className="head">

        <button
          className="brand"
          onClick={() => setMode('pilgrim')}
        >

          <b>TS</b>

          <span>
            <strong>TirthaSetu</strong>

            <small>
              Smart pilgrimage management
            </small>
          </span>

        </button>


        <div className="headTemple">

          <small>Temple</small>

          <TempleSelect
            value={temple}
            temples={temples}
            onChange={setTemple}
          />

        </div>


        <nav>

          <button
            className={
              mode === 'pilgrim'
                ? 'active'
                : ''
            }
            onClick={() => setMode('pilgrim')}
          >
            Pilgrim
          </button>


          <button
            className={
              mode === 'admin'
                ? 'active'
                : ''
            }
            onClick={() => setMode('admin')}
          >
            Control Room
          </button>


          <button
            onClick={() => setLang('EN')}
          >
            🌐
          </button>


          <button
            onClick={() => setMode('admin')}
          >
            ⚙
          </button>

        </nav>

      </div>

    </header>

  );

}


/* =========================
   PILGRIM PAGE
========================= */

function Pilgrim({
  temple,
  temples,
  setTemple,
  status,
  loading,
  open,
  notify
}) {

  const intel =
    status?.intelligence?.crowd_intelligence;

  const live =
    status?.intelligence?.live_data;

  const ai =
    status?.intelligence?.ai_prediction;

  const zones =
    status?.zones || [];

  const score =
    intel?.final_crowd_score;

  const risk =
    intel?.final_risk_level || '—';


  const showTraffic = async () => {

    try {

      const r = await api(
        `/api/traffic/${encodeURIComponent(temple)}`
      );

      const x = r.data?.[0];

      notify(

        x

          ?

          `${x.roadName}: ${x.trafficLevel} traffic${
            x.averageSpeed
              ? ` • ${x.averageSpeed} km/h`
              : ''
          }`

          :

          'No current traffic record is available for this temple.'

      );

    }

    catch (e) {

      notify(e.message);

    }

  };


  const showNotifications = async () => {

    try {

      const r = await api(
        `/api/notifications/unread/${encodeURIComponent(temple)}`
      );

      const x = r.data?.[0];

      notify(

        x

          ?

          `${x.title}: ${x.message}`

          :

          `No unread notifications for ${temple}.`

      );

    }

    catch (e) {

      notify(e.message);

    }

  };


  return (

    <main>

      {/* HERO */}

      <section className="hero wrap">

        <div>

          <div className="eyebrow">
            ● LIVE PILGRIM ASSISTANT
          </div>


          <h1>
            Plan your <em>darshan</em> around the crowd,
            not inside it.
          </h1>


          <p>
            Live ML crowd conditions, sensor-based parking,
            route guidance, smart darshan passes,
            accessibility and emergency help in one place.
          </p>


          <div className="actions">

            <TempleSelect
              value={temple}
              temples={temples}
              onChange={setTemple}
            />


            <Btn
              onClick={() => open('book')}
              disabled={!status}
            >
              ▣ Smart Darshan
            </Btn>


            <Btn
              kind="danger"
              onClick={() => open('sos')}
            >
              🚨 SOS
            </Btn>

          </div>


          <div className="trust">

            <span>
              ✓ ML-backed live status
            </span>

            <span>
              ✓ IoT telemetry
            </span>

            <span>
              ✓ Multilingual
            </span>

          </div>

        </div>


        {/* LIVE CARD */}

        <div className="liveCard">

          <div className="liveTop">

            <b>
              LIVE • {temple}
            </b>

            <span>
              {loading
                ? '● Updating'
                : '● Connected'}
            </span>

          </div>


          <div
            className="dial"
            style={{
              '--p':
                `${Number(score || 0) * 3.6}deg`
            }}
          >

            <div>

              <strong>

                {score === undefined
                  ? '—'
                  : `${score}%`}

              </strong>

              <span>
                fused crowd score
              </span>

            </div>

          </div>


          <div className="miniStats">

            <div>

              <b>
                {n(live?.total_current_people)}
              </b>

              <span>
                People in precinct
              </span>

            </div>


            <div>

              <b>
                {live?.parking_occupancy === undefined
                  ? '—'
                  : `${live.parking_occupancy}%`}
              </b>

              <span>
                Parking occupancy
              </span>

            </div>


            <div>

              <b>
                {ai?.predicted_visitors === undefined
                  ? '—'
                  : n(ai.predicted_visitors)}
              </b>

              <span>
                Predicted visitors
              </span>

            </div>

          </div>

        </div>

      </section>


      {/* STATS */}

      <section className="wrap statGrid">

        <Stat
          title="Crowd risk"
          value={risk}
          text={
            intel?.trend
              ? `${intel.trend.toLowerCase()} live flow`
              : 'Awaiting ML status'
          }
          tone={tone(risk)}
        />


        <Stat
          title="Peak zone"
          value={
            live?.highest_risk_zone || '—'
          }
          text={
            live?.max_zone_density === undefined
              ? 'Awaiting telemetry'
              : `${live.max_zone_density}% density`
          }
        />


        <Stat
          title="Parking"
          value={
            live?.parking_occupancy === undefined
              ? '—'
              : `${live.parking_occupancy}%`
          }
          text="Live sensor occupancy"
          tone={
            live?.parking_occupancy >= 85
              ? 'red'
              : 'green'
          }
        />


        <Stat
          title="Accessibility"
          value="On request"
          text="Priority + assistance"
          tone="green"
        />

      </section>


      {/* AI GUIDANCE */}

      <section className="wrap cols">

        <div className="card">

          <Section
            kicker="AI DECISION SUPPORT"
            title="Live visit guidance"
            sub="Guidance is generated from the trained model and current multi-zone telemetry."
          />


          <div className="recommend">

            <div>

              <span
                className={
                  'badge ' + tone(risk)
                }
              >
                ★ {
                  risk === '—'
                    ? 'LIVE STATUS'
                    : `${risk} STATUS`
                }
              </span>


              <h2>
                {
                  intel?.recommended_action ||
                  'Loading current guidance…'
                }
              </h2>


              <p>
                {
                  ai?.recommended_action ||
                  'The recommendation updates when live status is available.'
                }
              </p>


              <div className="confidence">

                <span>
                  ML forecast
                </span>

                <b>
                  {
                    ai?.crowd_percentage === undefined
                      ? '—'
                      : `${ai.crowd_percentage}%`
                  }
                </b>

              </div>

            </div>


            <MiniBars zones={zones} />

          </div>


          <div className="actions">

            <Btn
              onClick={() => open('book')}
              disabled={!status}
            >
              Reserve Smart Darshan
            </Btn>


            <Btn
              kind="soft"
              onClick={showNotifications}
            >
              🔔 Notify me
            </Btn>

          </div>

        </div>


        {/* PILGRIM SERVICES */}

        <div className="card">

          <Section
            kicker="PILGRIM SERVICES"
            title="Everything before you enter"
            sub="Guidance changes with the selected pilgrimage site."
          />


          <div className="featureGrid">

            <Tile
              t="🅿 Smart parking"
              s="Live occupancy"
              f={() =>
                notify(
                  live?.parking_occupancy === undefined
                    ? 'Parking telemetry is loading.'
                    : `Parking occupancy: ${live.parking_occupancy}%`
                )
              }
            />


            <Tile
              t="🧭 Route & gates"
              s="ML operational guidance"
              f={showTraffic}
            />


            <Tile
              t="♿ Accessibility"
              s="Priority + assistance"
              f={() => open('assist')}
            />


            <Tile
              t="🏥 Medical help"
              s="Emergency response"
              f={() => open('sos')}
            />


            <Tile
              t="🔔 Live alerts"
              s="Crowd threshold updates"
              f={showNotifications}
            />


            <Tile
              t="🌐 Languages"
              s="English • Hindi • Gujarati"
              f={() => open('lang')}
            />

          </div>

        </div>

      </section>


      {/* LIVE TEMPLE MAP */}

      <section className="wrap card">

        <Section
          kicker="ZONE MONITORING"
          title="Live temple map"
          sub="Real-time ML service telemetry by operational zone."
        />


        <div className="mapWrap">

          <div className="map">

            <div className="road r1"></div>
            <div className="road r2"></div>


            {zones.map((z, i) =>

              <div
                key={z.zone}
                className={
                  'zone ' + ztone(z.risk_level) + ' z' + i
                }
              >

                <b>
                  {String.fromCharCode(65 + i)}
                </b>

                <span>
                  {z.zone}
                </span>

                <small>
                  {z.crowd_density}%
                </small>

              </div>

            )}


            <span className="gate g1">
              Main Gate
            </span>

            <span className="gate g2">
              Temple Entry
            </span>

          </div>


          <div className="side">

            <div>
              🟢 Low <b>&lt;40%</b>
            </div>

            <div>
              🟡 Moderate <b>40–69%</b>
            </div>

            <div>
              🔴 High / critical <b>≥70%</b>
            </div>


            <div className="notice">

              <b>
                ⚠ {live?.highest_risk_zone || 'Live zone'}
                {' '}requires attention
              </b>


              <p>
                {
                  intel?.recommended_action ||
                  'Waiting for real-time telemetry.'
                }
              </p>


              <Btn
                kind="soft"
                onClick={() => open('guidance')}
              >
                Show guidance
              </Btn>

            </div>

          </div>

        </div>

      </section>


      {/* ACCESSIBILITY */}

      <section className="wrap banner">

        <div>

          <div className="eyebrow">
            ACCESSIBILITY BY DEFAULT
          </div>


          <h2>
            Make pilgrimage easier for every devotee.
          </h2>


          <p>
            Priority lanes, wheelchair assistance,
            multilingual information and emergency support.
          </p>

        </div>


        <div className="actions">

          <Btn
            kind="soft"
            onClick={() => open('assist')}
          >
            ♿ Request assistance
          </Btn>


          <Btn
            kind="danger"
            onClick={() => open('sos')}
          >
            🚨 Emergency SOS
          </Btn>

        </div>

      </section>

    </main>

  );

}


/* =========================
   GUIDANCE MODAL
========================= */

function Guidance({
  temple,
  status,
  close
}) {

  const intel =
    status?.intelligence?.crowd_intelligence;

  const live =
    status?.intelligence?.live_data;

  const ai =
    status?.intelligence?.ai_prediction;

  const risk =
    intel?.final_risk_level || '—';


  const action =
    intel?.recommended_action ||
    ai?.recommended_action ||
    'No current guidance available.';


  const zone =
    live?.highest_risk_zone ||
    '—';


  const density =
    live?.max_zone_density;


  const trend =
    intel?.trend ||
    '—';


  return (

    <Modal close={close}>

      <div className="eyebrow">
        AI GUIDANCE
      </div>


      <h2>
        Live Visit Guidance
      </h2>


      <p>
        Current operational guidance for <b>{temple}</b>.
      </p>


      <div className="guidanceGrid">

        <div className="guidanceItem">
          <span>Crowd Risk</span>
          <strong>{risk}</strong>
        </div>


        <div className="guidanceItem">
          <span>Highest Risk Zone</span>
          <strong>{zone}</strong>
        </div>


        <div className="guidanceItem">
          <span>Live Density</span>
          <strong>
            {density === undefined
              ? '—'
              : `${density}%`}
          </strong>
        </div>


        <div className="guidanceItem">
          <span>Crowd Trend</span>
          <strong>{trend}</strong>
        </div>

      </div>


      <div className="guidanceRecommendation">

        <div className="eyebrow">
          RECOMMENDED ACTION
        </div>


        <h3>
          {action}
        </h3>


        <p>
          Follow the recommended route and avoid the
          highest-density operational zone where possible.
        </p>

      </div>


      <Btn
        kind="full"
        onClick={close}
      >
        Got it
      </Btn>

    </Modal>

  );

}


/* =========================
   OTHER COMPONENTS
========================= */

const Tile = ({
  t,
  s,
  f
}) =>
  <button
    className="tile"
    onClick={f}
  >
    <b>{t}</b>
    <span>{s}</span>
    <i>→</i>
  </button>;


const MiniBars = ({ zones }) =>
  <div className="bars">

    {zones.map(z =>

      <div key={z.zone}>

        <i
          style={{
            height: `${z.crowd_density || 0}%`
          }}
        ></i>

        <span>
          {z.zone}
        </span>

      </div>

    )}

  </div>;


const LineChart = ({ zones }) =>

  <div className="lineChart">

    <div className="gridlines"></div>

    <div className="poly">

      {zones.map((z, i) =>

        <span
          key={z.zone}
          style={{
            left:
              (i / Math.max(zones.length - 1, 1)) * 100 + '%',

            bottom:
              `${z.crowd_density}%`
          }}
        ></span>

      )}

    </div>


    <div className="axis">

      {zones.map(z =>

        <span key={z.zone}>
          {z.zone}
        </span>

      )}

    </div>

  </div>;


const Resource = ({ a, c }) =>

  <div className="resource">

    <div>

      <b>{a}</b>

      <small>
        ML recommendation
      </small>

    </div>


    <strong>
      {c === undefined ? '—' : c}
    </strong>

  </div>;


const Sensor = ({ z }) =>

  <div className="sensor">

    <div>

      <b>{z.zone}</b>

      <small>
        {n(z.current_people)} people
      </small>

    </div>


    <strong>
      {z.crowd_density}%
    </strong>


    <span
      className={
        'badge ' + tone(z.risk_level)
      }
    >
      {z.risk_level}
    </span>

  </div>;


const Incident = ({ x }) =>

  <div className="incident">

    <span
      className={
        'badge ' + tone(x.risk_level)
      }
    >
      {x.risk_level}
    </span>


    <div>

      <b>{x.zone}</b>

      <small>
        {x.density}% • {x.status}
      </small>

    </div>


    <span>
      →
    </span>

  </div>;


/* =========================
   PARKING
========================= */

function Parking({
  temple,
  occupancy
}) {

  return (

    <div className="parking">

      <b>IoT</b>


      <div>

        <strong>
          {temple} parking
        </strong>

        <small>
          IoT occupancy
        </small>

      </div>


      <div className="prog">

        <i
          style={{
            width: `${occupancy || 0}%`
          }}
        ></i>

      </div>


      <span
        className={
          'badge ' +
          (
            occupancy >= 85
              ? 'red'
              : occupancy >= 40
                ? 'amber'
                : 'green'
          )
        }
      >

        {occupancy === undefined
          ? '—'
          : `${occupancy}%`}

      </span>

    </div>

  );

}


/* =========================
   ADMIN
========================= */

function Admin({
  temple,
  temples,
  setTemple,
  status,
  incidents,
  loading,
  refresh,
  notify
}) {

  const intel =
    status?.intelligence?.crowd_intelligence;

  const live =
    status?.intelligence?.live_data;

  const ai =
    status?.intelligence?.ai_prediction;

  const resources =
    status?.resource_recommendations || {};

  const zones =
    status?.zones || [];


  return (

    <main>

      <section className="wrap adminHead">

        <div>

          <div className="eyebrow">
            ● GOVERNMENT CONTROL ROOM
          </div>


          <h1>
            Temple Operations Dashboard
          </h1>


          <p>
            Monitor ML forecasts, IoT telemetry,
            safety and response from one command surface.
          </p>

        </div>


        <div className="actions">

          <TempleSelect
            value={temple}
            temples={temples}
            onChange={setTemple}
          />


          <Btn
            kind="soft"
            onClick={refresh}
          >
            ↻ {
              loading
                ? 'Refreshing…'
                : 'Refresh live data'
            }
          </Btn>

        </div>

      </section>


      <section className="wrap statGrid">

        <Stat
          title="Predicted visitors"
          value={n(ai?.predicted_visitors)}
          text="Random Forest forecast"
        />


        <Stat
          title="Live crowd"
          value={
            intel?.final_crowd_score === undefined
              ? '—'
              : `${intel.final_crowd_score}%`
          }
          text={
            intel?.final_risk_level ||
            'Awaiting ML status'
          }
          tone={tone(intel?.final_risk_level)}
        />


        <Stat
          title="Peak zone"
          value={
            live?.highest_risk_zone || '—'
          }
          text={
            live?.max_zone_density === undefined
              ? 'Awaiting telemetry'
              : `${live.max_zone_density}% density`
          }
          tone={
            live?.max_zone_density >= 85
              ? 'red'
              : 'amber'
          }
        />


        <Stat
          title="Sensor health"
          value={
            zones.length
              ? `${zones.length}/4`
              : '—'
          }
          text="Zones reporting"
          tone="green"
        />

      </section>


      <section className="wrap cols adminCols">

        <div className="card">

          <Section
            kicker="AI + IOT ANALYTICS"
            title="Crowd forecast & live density"
            sub="Trained Random Forest forecast fused 40/60 with live sensor density."
          />


          <LineChart zones={zones} />


          <div className="strip">

            <span>
              Trend
              <b>{intel?.trend || '—'}</b>
            </span>


            <span>
              AI forecast
              <b>
                {
                  ai?.crowd_percentage === undefined
                    ? '—'
                    : `${ai.crowd_percentage}%`
                }
              </b>
            </span>


            <span>
              Live average
              <b>
                {
                  live?.average_density === undefined
                    ? '—'
                    : `${live.average_density}%`
                }
              </b>
            </span>


            <span>
              Horizon
              <b>Next hour</b>
            </span>

          </div>

        </div>


        <div className="card">

          <Section
            kicker="AI RECOMMENDATION"
            title="Smart resource allocation"
            sub="ML resource-engine directives; no local resource calculation."
          />


          <Resource
            a="Security personnel"
            c={resources.security_personnel}
          />


          <Resource
            a="Medical personnel"
            c={resources.medical_personnel}
          />


          <Resource
            a="Additional gates"
            c={resources.additional_gates}
          />


          <Resource
            a="Emergency priority"
            c={status?.emergency_priority}
          />


          <Btn
            kind="full"
            onClick={() =>
              notify(
                status?.reasoning?.join(' ') ||
                'No ML recommendation is available.'
              )
            }
          >
            ✓ Review recommendation
          </Btn>

        </div>

      </section>


      <section className="wrap cols adminCols">

        <div className="card">

          <Section
            kicker="IOT / EDGE DATA"
            title="Sensor feed"
            sub="Live records supplied by the FastAPI IoT simulator."
          />


          {zones.map((z, i) =>

            <Sensor
              key={z.zone}
              z={z}
              i={i}
            />

          )}


          <div className="pipe">
            IoT simulator → FastAPI ML → Node gateway → Dashboard
          </div>

        </div>


        <div className="card">

          <Section
            kicker="SAFETY & RESPONSE"
            title="Incident center"
            sub="Active ML crowd incidents for this pilgrimage site."
          />


          {incidents.length

            ?

            incidents.map(x =>

              <Incident
                key={x.incident_id}
                x={x}
              />

            )

            :

            <p>
              No active ML incidents for {temple}.
            </p>

          }


          <Btn
            kind="danger full"
            onClick={refresh}
          >
            ↻ Refresh incident center
          </Btn>

        </div>

      </section>


      <section className="wrap card">

        <Section
          kicker="MOBILITY"
          title="Parking intelligence"
          sub="Live parking occupancy is sourced from the current IoT snapshot."
        />


        <div className="mob">

          <div>

            <Parking
              temple={temple}
              occupancy={live?.parking_occupancy}
            />

          </div>


          <div className="traffic">

            <b>OPERATIONS</b>

            <h3>
              Current ML directive
            </h3>


            <p>
              {
                status?.operations?.parking_action ||
                'Waiting for live resource guidance.'
              }
            </p>


            <p>
              {
                status?.operations?.queue_action ||
                'Waiting for live queue guidance.'
              }
            </p>

          </div>

        </div>

      </section>


      <section className="wrap card">

        <Section
          kicker="CROSS-TEMPLE COMMAND"
          title="Supported pilgrimage sites"
          sub="Select a site to load its own live ML status through Node."
        />


        {temples.map(x =>

          <button
            className="templeRow"
            key={x}
            onClick={() => setTemple(x)}
          >

            <div>

              <b>{x}</b>

              <span>
                Gujarat pilgrimage site
              </span>

            </div>


            <span>

              {x === temple
                ? 'Currently selected'
                : 'Load live status'}

            </span>


            <span>
              ML-supported
            </span>


            <span className="badge green">
              ACTIVE
            </span>


            <b>
              →
            </b>

          </button>

        )}

      </section>

    </main>

  );

}


/* =========================
   MODAL
========================= */

function Modal({
  children,
  close
}) {

  return (

    <div className="overlay">

      <div className="modal">

        {children}


        <button
          className="x"
          onClick={close}
        >
          ×
        </button>

      </div>

    </div>

  );

}


/* =========================
   BOOKING
   GOOGLE FORM QR FLOW
========================= */

function Booking({
  temple,
  status,
  close,
  notify
}) {

  const [size, setSize] = useState(2);

  const [priority, setPriority] = useState(false);

  const [booking, setBooking] = useState(null);


  const slot =

    status
      ?.intelligence
      ?.crowd_intelligence
      ?.final_risk_level === 'LOW'

      ?

      'Current low-risk window'

      :

      'Check live guidance before arrival';


  /*
    Generate QR for Google Form.
  */

  const generateRegistrationQR = () => {

    const qrUrl =
      'https://quickchart.io/qr?text=' +
      encodeURIComponent(GOOGLE_FORM_URL) +
      '&size=300';


    setBooking({

      temple,

      timeSlot: slot,

      familySize: Number(size),

      elderlyOrDisabled: priority,

      qrData: qrUrl

    });


    notify(
      'Registration QR generated.'
    );

  };


  return (

    <Modal close={close}>


      {!booking

        ?

        <>

          <div className="eyebrow">
            SMART DARSHAN
          </div>


          <h2>
            Start your darshan registration
          </h2>


          <p>
            {temple} • {slot}
          </p>


          <label>

            Number of pilgrims

            <input
              type="number"
              min="1"
              max="10"
              value={size}
              onChange={e =>
                setSize(e.target.value)
              }
            />

          </label>


          <label className="check">

            <input
              type="checkbox"
              checked={priority}
              onChange={e =>
                setPriority(e.target.checked)
              }
            />

            Priority assistance for elderly /
            differently-abled

          </label>


          <div className="notice">

            <b>
              How registration works
            </b>


            <p>

              1. Select your pilgrimage details.
              <br />

              2. Generate the registration QR.
              <br />

              3. Scan the QR code.
              <br />

              4. Complete the Google Form.
              <br />

              5. Submit your pilgrim details.

            </p>

          </div>


          <Btn
            kind="full"
            onClick={generateRegistrationQR}
          >
            ✓ Generate Registration QR
          </Btn>

        </>


        :

        <>

          <div className="eyebrow">
            REGISTRATION
          </div>


          <h2>
            Complete Your Darshan Registration
          </h2>


          <p>
            Scan the QR code below to open the
            TirthaSetu registration form.
          </p>


          <div className="ticket">


            <div>

              <span>
                Temple
              </span>

              <b>
                {booking.temple}
              </b>

            </div>


            <div>

              <span>
                Recommended Time
              </span>

              <b>
                {booking.timeSlot}
              </b>

            </div>


            <div>

              <span>
                Family Size
              </span>

              <b>
                {booking.familySize} pilgrims
              </b>

            </div>


            <div>

              <span>
                Priority Assistance
              </span>

              <b>
                {
                  booking.elderlyOrDisabled
                    ? 'Requested'
                    : 'Not requested'
                }
              </b>

            </div>


            <div className="qr">

              <img
                src={booking.qrData}
                alt="TirthaSetu registration QR code"
              />


              <small>
                Scan to open registration form
              </small>

            </div>


          </div>


          <div className="notice">

            <b>
              📱 Next step
            </b>


            <p>
              Scan this QR code using your phone camera.
              The Google Form will open. Enter all required
              pilgrim details and submit the form.
            </p>

          </div>


          <Btn
            kind="soft full"
            onClick={() => {

              window.open(
                GOOGLE_FORM_URL,
                '_blank'
              );

            }}
          >
            Open Registration Form
          </Btn>


          <Btn
            kind="full"
            onClick={close}
          >
            Close
          </Btn>

        </>

      }

    </Modal>

  );

}


/* =========================
   SOS
========================= */

function SOS({
  temple,
  close,
  notify
}) {

  const [sent, setSent] = useState(false);

  const [saving, setSaving] = useState(false);

  const [error, setError] = useState('');


  const submit = async type => {

    setSaving(true);
    setError('');


    try {

      await api(
        '/api/emergency',
        {
          method: 'POST',

          headers: {
            'Content-Type':
              'application/json'
          },

          body: JSON.stringify({

            temple,

            type,

            zone:
              'Main Temple Precinct',

            description:
              'Pilgrim SOS submitted from TirthaSetu.'

          })

        }
      );


      setSent(true);

      notify(
        'Emergency alert sent to the control room.'
      );

    }

    catch (e) {

      setError(e.message);

    }

    finally {

      setSaving(false);

    }

  };


  return (

    <Modal close={close}>

      <div className="eyebrow redText">
        EMERGENCY ASSISTANCE
      </div>


      <h2>
        {sent
          ? 'Alert sent to control room'
          : 'How can we help?'}
      </h2>


      {!sent

        ?

        <>

          <p>
            Select an incident type. This creates a
            Mongo-backed emergency alert through Node.
          </p>


          <div className="sosgrid">

            {[
              ['🚑 Medical', 'MEDICAL'],
              ['👮 Safety', 'SAFETY'],
              ['👶 Lost child', 'LOST_PERSON'],
              ['🚨 Crowd panic', 'CROWD_PANIC']

            ].map(([label, type]) =>

              <button
                key={type}
                disabled={saving}
                onClick={() => submit(type)}
              >
                {label} →
              </button>

            )}

          </div>


          {error &&

            <p className="redText">
              {error}
            </p>

          }


          <div className="loc">
            📍 Location: Main Temple Precinct
          </div>

        </>


        :

        <>

          <div className="success dangerS">
            !
          </div>


          <div className="sent">

            <b>
              Response teams notified
            </b>

            <span>
              Control room • nearest medical team • police
            </span>

          </div>


          <Btn
            kind="full"
            onClick={close}
          >
            Close
          </Btn>

        </>

      }

    </Modal>

  );

}


/* =========================
   ASSISTANCE
========================= */

function Assist({
  temple,
  close,
  notify
}) {

  const [sent, setSent] = useState(false);

  const [saving, setSaving] = useState(false);

  const [error, setError] = useState('');


  const submit = async description => {

    setSaving(true);
    setError('');


    try {

      await api(
        '/api/emergency',
        {
          method: 'POST',

          headers: {
            'Content-Type':
              'application/json'
          },

          body: JSON.stringify({

            temple,

            type: 'SAFETY',

            zone:
              'Accessibility desk',

            description:
              `Accessibility request: ${description}`

          })

        }
      );


      setSent(true);

      notify(
        'Assistance request sent.'
      );

    }

    catch (e) {

      setError(e.message);

    }

    finally {

      setSaving(false);

    }

  };


  return (

    <Modal close={close}>

      <div className="eyebrow">
        ACCESSIBILITY
      </div>


      <h2>
        {sent
          ? 'Assistance requested'
          : 'Priority support'}
      </h2>


      {!sent

        ?

        <>

          <p>
            Choose support needed at {temple}.
          </p>


          <div className="assist">

            {[

              'Wheelchair assistance',
              'Priority queue entry',
              'Elderly guidance',
              'Medical escort'

            ].map(x =>

              <button
                disabled={saving}
                key={x}
                onClick={() => submit(x)}
              >

                {x}

                <span>
                  →
                </span>

              </button>

            )}

          </div>


          {error &&

            <p className="redText">
              {error}
            </p>

          }

        </>


        :

        <>

          <div className="success">
            ✓
          </div>


          <p>
            Your request is visible in the
            control-room workflow.
          </p>


          <Btn
            kind="full"
            onClick={close}
          >
            Done
          </Btn>

        </>

      }

    </Modal>

  );

}


/* =========================
   LANGUAGE
========================= */

function Lang({
  value,
  set,
  close
}) {

  return (

    <Modal close={close}>

      <div className="eyebrow">
        LANGUAGE
      </div>


      <h2>
        Choose your language
      </h2>


      <div className="assist">

        {['EN', 'हिं', 'ગુ'].map(x =>

          <button
            key={x}
            onClick={() => {

              set(x);
              close();

            }}

            className={
              value === x
                ? 'selected'
                : ''
            }
          >

            {x}

            <span>
              →
            </span>

          </button>

        )}

      </div>

    </Modal>

  );

}


/* =========================
   START APP
========================= */

createRoot(
  document.getElementById('root')
).render(
  <App />
);