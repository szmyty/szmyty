(function () {
  const container = document.getElementById("execution-observatory");
  if (!container) {
    return;
  }

  const status = container.querySelector("[data-observatory-status]");
  const motionButton = document.querySelector("[data-observatory-toggle-motion]");
  const reduceMotionButton = document.querySelector("[data-observatory-reduce-motion]");
  const timelineStages = Array.from(document.querySelectorAll("[data-stage-type]"));
  const stageNodes = timelineStages.map((el) => ({
    label: el.querySelector("strong")?.textContent?.trim() ?? "Stage",
    element: el,
  }));
  const fallbackList = container.querySelector(".trace-observatory-fallback");
  const query = new URLSearchParams(window.location.search);

  const setStatus = (message) => {
    if (status) {
      status.textContent = message;
    }
  };

  if (stageNodes.length === 0) {
    setStatus("Timeline data is unavailable.");
    return;
  }

  if (!("WebGLRenderingContext" in window)) {
    setStatus("WebGL is unavailable. Showing semantic fallback.");
    return;
  }

  const previewMode = query.get("preview") === "1";
  const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  let reduceMotion = previewMode || prefersReducedMotion.matches;
  let paused = reduceMotion;
  let activeIndex = 0;

  const updateMotionButtons = () => {
    if (motionButton) {
      motionButton.textContent = paused ? "Resume orbit" : "Pause orbit";
      motionButton.setAttribute("aria-pressed", paused ? "true" : "false");
    }
    if (reduceMotionButton) {
      reduceMotionButton.setAttribute("aria-pressed", reduceMotion ? "true" : "false");
    }
  };

  const focusStage = (index) => {
    activeIndex = (index + stageNodes.length) % stageNodes.length;
    const stage = stageNodes[activeIndex];
    stage.element.scrollIntoView({
      block: "nearest",
      behavior: reduceMotion ? "auto" : "smooth",
    });
    stage.element.focus({ preventScroll: true });
    setStatus(`Focused stage: ${stage.label}`);
  };

  if (motionButton) {
    motionButton.addEventListener("click", () => {
      paused = !paused;
      updateMotionButtons();
      setStatus(paused ? "Orbit paused." : "Orbit resumed.");
    });
  }

  if (reduceMotionButton) {
    reduceMotionButton.addEventListener("click", () => {
      reduceMotion = !reduceMotion;
      paused = reduceMotion || paused;
      updateMotionButtons();
      setStatus(reduceMotion ? "Reduced motion enabled." : "Reduced motion disabled.");
    });
  }

  container.addEventListener("keydown", (event) => {
    if (event.key === "ArrowRight") {
      event.preventDefault();
      focusStage(activeIndex + 1);
    } else if (event.key === "ArrowLeft") {
      event.preventDefault();
      focusStage(activeIndex - 1);
    } else if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      stageNodes[activeIndex].element.querySelector("a")?.click();
    }
  });

  if (fallbackList) {
    fallbackList.hidden = false;
  }
  updateMotionButtons();

  const webglProbe = document.createElement("canvas");
  if (!webglProbe.getContext("webgl2") && !webglProbe.getContext("webgl")) {
    setStatus("WebGL context failed. Showing semantic fallback.");
    return;
  }

  const boot = async () => {
    try {
      const THREE = await import("./vendor/three.module.min.js");
      const scene = new THREE.Scene();
      scene.background = new THREE.Color(0x06080f);

      const width = Math.max(320, container.clientWidth);
      const height = Math.max(320, container.clientHeight);
      const camera = new THREE.PerspectiveCamera(52, width / height, 0.1, 100);
      camera.position.set(0, 0, 10);

      const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
      renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
      renderer.setSize(width, height);
      renderer.outputColorSpace = THREE.SRGBColorSpace;
      container.appendChild(renderer.domElement);

      scene.add(new THREE.AmbientLight(0xffffff, 0.6));
      const point = new THREE.PointLight(0x7dd3fc, 1.2, 100);
      point.position.set(2, 4, 6);
      scene.add(point);

      const ringRadius = 4;
      const meshes = [];
      const lineMaterial = new THREE.LineBasicMaterial({
        color: 0x4f46e5,
        transparent: true,
        opacity: 0.55,
      });
      const sphereGeometry = new THREE.SphereGeometry(0.28, 24, 24);

      stageNodes.forEach((stage, index) => {
        const angle = (index / stageNodes.length) * Math.PI * 2;
        const x = Math.cos(angle) * ringRadius;
        const y = Math.sin(angle) * ringRadius;
        const material = new THREE.MeshStandardMaterial({
          color: index === 0 ? 0x7dd3fc : 0xa78bfa,
          emissive: 0x111827,
          metalness: 0.2,
          roughness: 0.35,
        });
        const sphere = new THREE.Mesh(sphereGeometry, material);
        sphere.position.set(x, y, 0);
        sphere.userData.stageIndex = index;
        meshes.push(sphere);
        scene.add(sphere);
      });

      for (let i = 0; i < meshes.length; i += 1) {
        const start = meshes[i].position;
        const end = meshes[(i + 1) % meshes.length].position;
        const geometry = new THREE.BufferGeometry().setFromPoints([start, end]);
        scene.add(new THREE.Line(geometry, lineMaterial));
      }

      const raycaster = new THREE.Raycaster();
      const pointer = new THREE.Vector2();
      const tooltip = document.createElement("p");
      tooltip.className = "trace-observatory-status";
      tooltip.setAttribute("aria-live", "polite");
      container.appendChild(tooltip);

      const highlight = (index) => {
        meshes.forEach((mesh, meshIndex) => {
          const active = meshIndex === index;
          mesh.material.color.set(active ? 0x7dd3fc : 0xa78bfa);
          mesh.scale.setScalar(active ? 1.35 : 1);
        });
        activeIndex = index;
        tooltip.textContent = `Selected: ${stageNodes[index].label}`;
      };

      const onPointer = (event) => {
        const rect = renderer.domElement.getBoundingClientRect();
        pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
        raycaster.setFromCamera(pointer, camera);
        const [hit] = raycaster.intersectObjects(meshes);
        if (hit) {
          highlight(Number(hit.object.userData.stageIndex ?? 0));
        }
      };

      renderer.domElement.addEventListener("pointermove", onPointer);
      renderer.domElement.addEventListener("click", (event) => {
        onPointer(event);
        focusStage(activeIndex);
      });

      const onResize = () => {
        const nextWidth = Math.max(320, container.clientWidth);
        const nextHeight = Math.max(320, container.clientHeight);
        camera.aspect = nextWidth / nextHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(nextWidth, nextHeight);
      };

      const animate = (timestamp) => {
        if (!container.isConnected) {
          window.removeEventListener("resize", onResize);
          renderer.dispose();
          return;
        }
        if (!paused && !reduceMotion) {
          scene.rotation.z = timestamp * 0.00012;
        }
        renderer.render(scene, camera);
        requestAnimationFrame(animate);
      };

      window.addEventListener("resize", onResize);
      highlight(0);
      setStatus("Orbit ready. Use arrow keys to move between stages.");
      if (fallbackList) {
        fallbackList.hidden = true;
      }
      requestAnimationFrame(animate);
    } catch {
      setStatus("Interactive orbit is unavailable. Showing semantic fallback.");
    }
  };

  if ("requestIdleCallback" in window) {
    window.requestIdleCallback(boot, { timeout: 1200 });
  } else {
    window.setTimeout(boot, 600);
  }
})();
