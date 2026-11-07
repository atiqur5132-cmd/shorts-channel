    // ---- shorts master template: shared motion (injected by tools/inject_common.py) ----
    // Every helper adds tweens to `tl` at an absolute scene time; all are seek-safe.
    const M = {
      // ground: one slow camera push across a shot (continuous motion on the photo, never on titles)
      push(tl, sel, t, dur, from = 1.0, to = 1.07, x = 0, y = 0) {
        tl.fromTo(sel, { scale: from, x: 0, y: 0 }, { scale: to, x, y, duration: dur, ease: "power1.inOut" }, t);
      },
      // hard-cut arrival: the shot lands slightly large and settles
      settle(tl, sel, t, from = 1.14) {
        tl.fromTo(sel, { scale: from }, { scale: 1, duration: 0.5, ease: "expo.out", immediateRender: false }, t);
      },
      // title slam: big -> landed, then dead still
      slam(tl, sel, t, from = 1.7) {
        tl.fromTo(sel, { scale: from, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.2, ease: "power4.out" }, t);
      },
      // per-word blur-in, 0.067 s apart, no translate
      words(tl, sel, t, gap = 0.067) {
        tl.fromTo(sel, { opacity: 0, filter: "blur(10px)" },
          { opacity: 1, filter: "blur(0px)", duration: 0.14, ease: "power2.out", stagger: gap }, t);
      },
      // rubber stamp: drops from above the paper, lands with a small overshoot
      stamp(tl, sel, t, rot = -6) {
        tl.fromTo(sel, { scale: 2.3, rotation: rot - 12, opacity: 0 },
          { scale: 1, rotation: rot, opacity: 1, duration: 0.16, ease: "power4.in" }, t);
      },
      // a 6-frame frame shake on a wrapper, seek-safe (baseline set once by the caller)
      shake(tl, sel, t, amp = 16) {
        tl.to(sel, {
          keyframes: [
            { x: -amp, y: amp * 0.5, duration: 0.033 }, { x: amp * 0.8, y: -amp * 0.6, duration: 0.033 },
            { x: -amp * 0.5, y: amp * 0.4, duration: 0.033 }, { x: amp * 0.3, y: -amp * 0.2, duration: 0.033 },
            { x: 0, y: 0, duration: 0.06 },
          ], ease: "none",
        }, t);
      },
      // card toss-in: from below with rotation, settles on a long tail
      cardIn(tl, sel, t, rotFrom = 9, rotTo = -2, fromY = 300) {
        tl.fromTo(sel, { y: fromY, rotation: rotFrom, opacity: 0 },
          { y: 0, rotation: rotTo, opacity: 1, duration: 0.55, ease: "expo.out" }, t);
      },
      // exit: one smooth accelerating move
      exitDown(tl, sel, t, dur = 0.3) {
        tl.to(sel, { y: 380, opacity: 0, duration: dur, ease: "power3.in" }, t);
      },
      // number counter written into an element's text
      count(tl, el, t, dur, from, to, fmt) {
        const o = { v: from };
        tl.fromTo(o, { v: from }, {
          v: to, duration: dur, ease: "power3.out",
          onUpdate: () => { document.querySelector(el).textContent = fmt(o.v); },
        }, t);
      },
      // strike line drawing across (scaleX from the left)
      strike(tl, sel, t) {
        tl.fromTo(sel, { scaleX: 0 }, { scaleX: 1, duration: 0.22, ease: "power4.out" }, t);
      },
    };
    // ---- end shared motion ----
