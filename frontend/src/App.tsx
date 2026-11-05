import { useState } from "react";
import "./App.css";
import UserLayer from "./UserLayer";

const nav = [
  ["OPERATIONS", "Dashboard", "⌂"], ["", "Markets", "◈"], ["", "Watchlist", "☆"],
  ["", "Portfolio", "◫"], ["", "Positions", "⇄"], ["", "Orders", "≡"],
  ["AI", "AI Command Center", "✦"], ["", "Signals", "⌁"], ["", "Agents", "◎"], ["", "Memory", "◉"],
  ["INFRASTRUCTURE", "Harness", "◇"], ["", "MCP Tools", "⌘"],
  ["RISK", "Risk Center", "△"], ["", "Execution", "↗"],
  ["SYSTEM", "Accounts", "▣"], ["", "Broker Connections", "⌁"], ["", "Work 200 Verification", "✓"], ["", "Settings", "⚙"],
];

const assets = [
  ["XAUUSD","Gold / US Dollar","2,672.84","+1.28%","LONG","MEDIUM","MT5 · Exness"],
  ["BTCUSDT","Bitcoin / Tether","118,420.50","+0.84%","LONG","HIGH","OKX · Perp"],
  ["EURUSD","Euro / US Dollar","1.17482","-0.21%","WATCH","LOW","MT5 · ECN"],
  ["US100","Nasdaq 100","24,891.20","+0.43%","WATCH","MEDIUM","CFD · Prime"],
];

const pipeline = [
  ["01","Market Data","12 ms","done"],["02","Context","8 ms","done"],["03","Agents","31 ms","done"],
  ["04","Planner","18 ms","active"],["05","Trade Plan","—","wait"],["06","Risk Engine","—","wait"],["07","Execution","—","wait"],
];

function Chart() {
  return <div className="chart">
    <div className="gridlines" />
    <svg viewBox="0 0 800 260" preserveAspectRatio="none">
      <defs><linearGradient id="fill" x1="0" x2="0" y1="0" y2="1">
        <stop offset="0" stopColor="#22d3ee" stopOpacity=".22"/><stop offset="1" stopColor="#22d3ee" stopOpacity="0"/>
      </linearGradient></defs>
      <path d="M0 205 C35 194 58 214 91 180 S148 170 182 178 S220 130 260 151 S310 138 348 118 S390 150 425 112 S470 126 510 88 S550 106 586 67 S625 82 663 51 S714 69 754 35 S780 46 800 22 L800 260 L0 260Z" fill="url(#fill)"/>
      <path d="M0 205 C35 194 58 214 91 180 S148 170 182 178 S220 130 260 151 S310 138 348 118 S390 150 425 112 S470 126 510 88 S550 106 586 67 S625 82 663 51 S714 69 754 35 S780 46 800 22" fill="none" stroke="#22d3ee" strokeWidth="3"/>
      <path d="M0 225 C50 214 80 231 120 211 S180 220 225 191 S275 204 320 182 S370 192 420 163 S475 181 520 146 S580 160 625 128 S690 143 735 103 S775 112 800 94" fill="none" stroke="#a78bfa" strokeOpacity=".55" strokeWidth="2" strokeDasharray="6 8"/>
    </svg>
    <span className="axis a1">2,680</span><span className="axis a2">2,650</span><span className="axis a3">2,620</span>
    <div className="chart-tip"><b>AI SIGNAL · LONG</b><small>84.6% confidence</small><small>Entry zone 2,668–2,674</small></div>
    <div className="xaxis"><span>08:00</span><span>09:00</span><span>10:00</span><span>11:00</span><span>12:00</span></div>
  </div>;
}

function Metric({name,value,sub,tone}:{name:string,value:string,sub:string,tone:string}) {
  return <div className={`metric ${tone}`}><div className="metric-top"><span>{name}</span><i/></div><strong>{value}</strong><small>{sub}</small></div>;
}

export default function App() {
  const [active,setActive]=useState("Dashboard");
  const [menu,setMenu]=useState(false);
  const [command,setCommand]=useState(false);

  return <div className="app">
    <aside className={`sidebar ${menu?"open":""}`}>
      <div className="brand"><div className="logo"><span/></div><div><b>AI TRADE</b><small>OPERATING SYSTEM <em>V3</em></small></div></div>
      <div className="health"><i/><div><b>System Nominal</b><small>Harness · MCP · Risk online</small></div><strong>99.8%</strong></div>
      <nav>{nav.map(([section,label,icon], _i)=><div key={label}>
        {section && <h6>{section}<span/></h6>}
        <button className={active===label?"selected":""} onClick={()=>{setActive(label);setMenu(false)}}><span>{icon}</span>{label}{label==="Signals"&&<em>4</em>}</button>
      </div>)}</nav>
      <div className="account"><div className="avatar">B</div><div><b>Main Account</b><small>MT5 · Exness Prime</small></div><span>⌄</span></div>
    </aside>
    {menu&&<button className="backdrop" onClick={()=>setMenu(false)}/>}
    <main>
      <header><div className="lefthead"><button className="hamb" onClick={()=>setMenu(true)}>☰</button><span>AI TRADE</span><i>/</i><b>{active}</b></div>
        <div className="top-actions"><button className="command" onClick={()=>setCommand(true)}>⌘ <span>Command</span><kbd>⌘ K</kbd></button><label className="status amber">● DEMO DATA / DỮ LIỆU MẪU</label><button className="bell">◌</button><div className="topavatar">B</div></div>
      </header>
      <div className="content">
        {active === "Broker Connections" || active === "Work 200 Verification" ? <UserLayer page={active} /> : <>
        <div role="status" style={{padding:"10px 14px",border:"1px solid #f59e0b55",borderRadius:8,color:"#f6cf8a",background:"#f59e0b0d",fontSize:12,marginBottom:12}}>BAOXTRA V3.1 — DEMO / MOCK DATA ONLY. No live broker connection, no verified P&amp;L, no backend kill switch. REVIEW_ONLY.</div>
        <section className="heading"><div><label>— COMMAND OVERVIEW</label><h1>Good morning, <span>Trader.</span></h1><p>Your AI trading system is operating within configured safety boundaries.</p></div><div className="heading-buttons"><b>● Markets Open</b><button onClick={()=>setCommand(true)}>✦ AI Command</button></div></section>

        <section className="metrics">
          <Metric name="TOTAL EQUITY" value="$124,860.42" sub="vs. previous session  +2.84%" tone="cyan"/>
          <Metric name="UNREALIZED P&L" value="+$3,842.18" sub="7 active positions  +3.18%" tone="green"/>
          <Metric name="AI WIN RATE" value="84.6%" sub="65 validated signals" tone="purple"/>
          <Metric name="DRAWDOWN GUARD" value="4.2%" sub="limit · 8.0% configured" tone="amber"/>
        </section>

        <section className="two-col">
          <article className="panel chart-panel"><div className="panel-head"><div><label>LIVE MARKET</label><h2>XAUUSD <small>● LIVE</small></h2><p>Gold / US Dollar · MT5 · Exness Prime</p></div><div className="timeframes"><button className="on">M15</button><button>H1</button><button>H4</button><button>D1</button></div></div>
            <div className="price"><b>2,672.84</b><span>+33.76 (+1.28%)</span></div><Chart/><footer><span>━ Price　<span className="purple">┄ AI projection</span></span><span>REGIME　<b>BULLISH</b></span></footer>
          </article>
          <article className="panel intelligence"><div className="panel-head"><div><label>AI MARKET INTELLIGENCE</label><h2>Consensus</h2></div><strong className="confidence">84.6%</strong></div>
            <div className="consensus"><div className="ring"><div><b>LONG</b><small>AI BIAS</small></div></div><p><b>High confidence</b><br/>4 agents agree on current directional structure.</p></div>
            <div className="agents">{[["Macro","LONG","91%"],["Order Flow","LONG","86%"],["Technical","LONG","88%"],["Risk Guard","PASS","92%"]].map(x=><div key={x[0]}><span>{x[0]}</span><b>{x[1]}</b><small>{x[2]}</small></div>)}</div>
            <div className="ainote">✦ <span>Momentum remains positive while volatility is inside the configured risk envelope.</span></div>
          </article>
        </section>

        <section className="two-col lower">
          <article className="panel"><div className="panel-head"><div><label>MARKET WATCH</label><h2>Watchlist</h2></div><button className="link" onClick={()=>setActive("Markets")}>View markets →</button></div>
            <div className="watch-head"><span>ASSET</span><span>PRICE</span><span>24H</span><span>AI SIGNAL</span><span>RISK</span></div>
            {assets.map(a=><button className="watch-row" key={a[0]} onClick={()=>setActive("Markets")}><div className="asset"><i>{a[0][0]}</i><b>{a[0]}<small>{a[1]}</small></b></div><div><b>{a[2]}</b><small>{a[6]}</small></div><span className={a[3][0]==="-"?"negative":"positive"}>{a[3]}</span><em className={`signal ${a[4].toLowerCase()}`}>{a[4]}</em><em className={`risk ${a[5].toLowerCase()}`}>{a[5]}</em></button>)}
          </article>
          <article className="panel"><div className="panel-head"><div><label>AI ORCHESTRATION</label><h2>Decision Pipeline</h2></div><span className="telemetry">92 ms total</span></div><div className="pipeline">{pipeline.map((p,i)=><div className={`step ${p[3]}`} key={p[0]}><i>{p[3]==="done"?"✓":p[3]==="active"?"●":p[0]}</i><div><b>{p[1]}</b><small>{p[3]==="done"?"Complete":p[3]==="active"?"Processing":"Waiting"}</small></div><span>{p[2]}</span>{i<pipeline.length-1&&<hr/>}</div>)}</div></article>
        </section>

        <section className="two-col bottom">
          <article className="panel"><div className="panel-head"><div><label>AUDIT STREAM</label><h2>AI Decision Timeline</h2></div><button className="link" onClick={()=>setActive("Harness")}>Open audit →</button></div><div className="timeline">{[["09:31:04","Market data received","XAUUSD M15 · liquidity normal","blue"],["09:31:05","Technical Agent completed","Trend structure: bullish","cyan"],["09:31:06","Macro Agent completed","USD pressure easing","purple"],["09:31:07","Planner is evaluating","Building candidate trade plan","amber"]].map(e=><div key={e[0]}><i className={e[3]}/><time>{e[0]}</time><p><b>{e[1]}</b><small>{e[2]}</small></p><span>•••</span></div>)}</div></article>
          <article className="panel risk-panel"><div className="panel-head"><div><label>RISK ENGINE</label><h2>Guard Status</h2></div><strong className="nominal">● NOMINAL</strong></div><div className="riskbar"><div><span>42%</span></div><p><b>Risk utilization</b><small>4.2% / 10.0% maximum</small></p></div><div className="riskstats"><div><span>Daily Loss</span><b>$182 / $1,000</b></div><div><span>Margin</span><b>18.4%</b></div><div><span>Exposure</span><b>$42,680</b></div></div><button className="kill" disabled title="UI preview only — backend kill switch not implemented">⏻ STOP CONTROL UNAVAILABLE — UI ONLY</button></article>
        </section>
        </>}
      </div>
    </main>

    {command&&<div className="overlay" onClick={()=>setCommand(false)}><div className="command-modal" onClick={e=>e.stopPropagation()}><div className="search">⌕<input autoFocus placeholder="Search assets, modules, commands..."/><kbd>ESC</kbd></div><label>QUICK ACTIONS</label>{[["✦","Analyze XAUUSD","AI Command Center"],["△","Open Risk Center","Risk Center"],["↗","Open Execution Center","Execution"],["◉","Search Memory","Memory"]].map(x=><button key={x[1]} onClick={()=>{setActive(x[2]);setCommand(false)}}><span>{x[0]}　{x[1]}</span><kbd>↵</kbd></button>)}</div></div>}
  </div>;
}
