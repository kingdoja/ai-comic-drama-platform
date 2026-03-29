const navItems = [
  "Overview",
  "Story Bible",
  "Characters",
  "Episode Plan",
  "Storyboard",
  "Preview & QA",
  "Publish",
];

const shots = [
  { code: "SHOT_01", label: "女主初登场", duration: "6s" },
  { code: "SHOT_02", label: "反派挑衅", duration: "5s" },
  { code: "SHOT_03", label: "身份伏笔", duration: "7s" },
];

export default function HomePage() {
  return (
    <main className="shell">
      <div className="topbar">
        <div>
          <div className="badge">Editorial Control Room</div>
          <h1 className="section-title" style={{ marginTop: 12 }}>AI 漫剧创作者工作台</h1>
          <p className="subtle">把女频网文 / 短剧脚本素材，改编成可发布的竖屏漫剧单集包。</p>
        </div>
        <button className="btn primary">从素材改编</button>
      </div>

      <section className="hero">
        <article className="panel hero-card">
          <div className="mono">PHASE 1 / MVP WORKSPACE</div>
          <h2 className="section-title" style={{ fontSize: 34, marginTop: 10 }}>先把单集包稳定做出来</h2>
          <p className="subtle">
            当前骨架已经围绕工作台、状态推进、分镜可视化、QA 和局部重跑建立。下一步只需要把真实接口和 workflow 接上去。
          </p>
          <div className="action-row">
            <button className="btn primary">查看项目工作台</button>
            <button className="btn">查看文档中心</button>
            <button className="btn">检查 API 健康状态</button>
          </div>
        </article>

        <article className="panel hero-card preview-well">
          <div className="mono">9:16 PREVIEW STAGE / EP01</div>
          <div className="phone">
            <div>
              <h3 className="phone-title">她不是弃女</h3>
              <div className="phone-sub">73 秒 · 配音 v2 · QA 待确认</div>
            </div>
          </div>
        </article>
      </section>

      <section className="grid">
        <aside className="panel sidebar">
          <div className="mono">PROJECT NAV</div>
          <div className="sidebar-nav">
            {navItems.map((item, index) => (
              <div key={item} className={index === 0 ? "sidebar-item active" : "sidebar-item"}>
                {item}
              </div>
            ))}
          </div>
        </aside>

        <section className="panel main">
          <div className="stagebar">
            <span className="done" />
            <span className="done" />
            <span className="active" />
            <span />
            <span />
          </div>
          <div className="mono">CURRENT STAGE / STORYBOARD</div>
          <h2 className="section-title" style={{ fontSize: 26, marginTop: 10 }}>当前阶段：分镜确认</h2>
          <p className="subtle" style={{ marginBottom: 18 }}>
            这一步是整个单集包的视觉中枢。镜头一旦锁定，后面的关键帧、字幕、配音和 QA 都会围绕这里展开。
          </p>
          <div className="storyboard-grid">
            {shots.map((shot) => (
              <article key={shot.code} className="shot-card">
                <div className="shot-thumb" />
                <div className="shot-meta">
                  <strong>{shot.code}</strong>
                  <div className="subtle" style={{ marginTop: 6 }}>{shot.label}</div>
                  <div className="mono" style={{ marginTop: 10 }}>{shot.duration} / READY FOR RENDER</div>
                </div>
              </article>
            ))}
          </div>
        </section>

        <aside className="panel assist">
          <div className="mono">AI ASSIST + QA</div>
          <div className="kpi" style={{ marginTop: 16 }}>
            <div className="kpi-card">
              <strong>下一步</strong>
              <div className="subtle" style={{ marginTop: 6 }}>生成关键帧并保持角色服装锚点一致。</div>
            </div>
            <div className="kpi-card">
              <strong>风险提示</strong>
              <div className="subtle" style={{ marginTop: 6 }}>SHOT_03 预计超时 2 秒，建议缩短停顿。</div>
            </div>
            <div className="kpi-card">
              <strong>QA 目标</strong>
              <div className="subtle" style={{ marginTop: 6 }}>通过率 85% 以上再进入导出。</div>
            </div>
          </div>
        </aside>
      </section>
    </main>
  );
}
