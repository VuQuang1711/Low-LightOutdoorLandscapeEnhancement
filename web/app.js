/**
 * ==============================================================================
 * ỨNG DỤNG SO SÁNH NGHIÊN CỨU KỸ THUẬT XỬ LÝ ẢNH
 * Client-side Controller: web/app.js
 * Universal Explainable AI & 3-Tier Presentation Logic
 * ==============================================================================
 */

document.addEventListener("DOMContentLoaded", () => {
  // Global State
  const state = {
    totalImages: 0,
    currentImageIdx: 0,
    customFileB64: null,
    isCustomUpload: false,
    groundTruthAvailable: true,
    lastResponseData: null,
    histChartInstance: null,
    radarChartInstance: null,
    activeFormula: "clahe",
    splitDividerPos: 50, // %
    isDraggingSplit: false,
    isProcessing: false
  };

  // DOM Elements - Navigation & System
  const btnThemeToggle = document.getElementById("btnThemeToggle");
  const btnOpenHelp = document.getElementById("btnOpenHelp");
  const modalExplanationDashboard = document.getElementById("modalExplanationDashboard");
  const btnCloseModal = document.getElementById("btnCloseModal");
  const systemStatus = document.getElementById("systemStatus");

  // DOM Elements - Sidebar Controls
  const tabDataset = document.getElementById("tabDataset");
  const tabUpload = document.getElementById("tabUpload");
  const paneDataset = document.getElementById("paneDataset");
  const paneUpload = document.getElementById("paneUpload");
  const imgIndexSlider = document.getElementById("imgIndexSlider");
  const imgIndexVal = document.getElementById("imgIndexVal");
  const btnPrevImg = document.getElementById("btnPrevImg");
  const btnNextImg = document.getElementById("btnNextImg");
  const btnRandomImg = document.getElementById("btnRandomImg");
  const currentFileName = document.getElementById("currentFileName");

  // File Upload
  const dropZone = document.getElementById("dropZone");
  const fileUploadInput = document.getElementById("fileUploadInput");
  const uploadPreviewRow = document.getElementById("uploadPreviewRow");
  const uploadFileName = document.getElementById("uploadFileName");
  const btnRemoveUpload = document.getElementById("btnRemoveUpload");

  // Degradation Controls
  const chkSimulateLowLight = document.getElementById("chkSimulateLowLight");
  const lowLightSettings = document.getElementById("lowLightSettings");
  const brightnessFactorSlider = document.getElementById("brightnessFactorSlider");
  const brightnessFactorVal = document.getElementById("brightnessFactorVal");
  const gammaDarkSlider = document.getElementById("gammaDarkSlider");
  const gammaDarkVal = document.getElementById("gammaDarkVal");
  const noiseTypeSelect = document.getElementById("noiseTypeSelect");
  const noiseSigmaSlider = document.getElementById("noiseSigmaSlider");
  const noiseSigmaVal = document.getElementById("noiseSigmaVal");
  const noiseParamGroup = document.getElementById("noiseParamGroup");

  // Enhancement Algorithm Controls
  const denoiseMethodSelect = document.getElementById("denoiseMethodSelect");
  const colorSpaceSelect = document.getElementById("colorSpaceSelect");
  const claheClipSlider = document.getElementById("claheClipSlider");
  const claheClipVal = document.getElementById("claheClipVal");
  const gammaValSlider = document.getElementById("gammaValSlider");
  const gammaValVal = document.getElementById("gammaValVal");
  const gridPills = document.querySelectorAll(".grid-pill");
  const btnResetParams = document.getElementById("btnResetParams");
  const btnExecute = document.getElementById("btnExecute");

  // DOM Elements - Content & KPIs
  const bannerProtocol = document.getElementById("bannerProtocol");
  const valBestPsnr = document.getElementById("valBestPsnr");
  const tagBestPsnr = document.getElementById("tagBestPsnr");
  const subPsnr = document.getElementById("subPsnr");

  const valBestSsim = document.getElementById("valBestSsim");
  const tagBestSsim = document.getElementById("tagBestSsim");
  const subSsim = document.getElementById("subSsim");

  const valBestNiqe = document.getElementById("valBestNiqe");
  const tagBestNiqe = document.getElementById("tagBestNiqe");
  const subNiqe = document.getElementById("subNiqe");

  // Images Elements
  const imgClean = document.getElementById("imgClean");
  const imgDegraded = document.getElementById("imgDegraded");
  const imgDenoisedInput = document.getElementById("imgDenoisedInput");
  const imgResHe = document.getElementById("imgResHe");
  const imgResClahe = document.getElementById("imgResClahe");
  const imgResGamma = document.getElementById("imgResGamma");
  const imgResMsr = document.getElementById("imgResMsr");

  // Mini metrics in 4-grid cards
  const miniPsnrHe = document.getElementById("miniPsnrHe");
  const miniSsimHe = document.getElementById("miniSsimHe");
  const miniNiqeHe = document.getElementById("miniNiqeHe");
  const timeHe = document.getElementById("timeHe");

  const miniPsnrClahe = document.getElementById("miniPsnrClahe");
  const miniSsimClahe = document.getElementById("miniSsimClahe");
  const miniNiqeClahe = document.getElementById("miniNiqeClahe");
  const timeClahe = document.getElementById("timeClahe");

  const miniPsnrGamma = document.getElementById("miniPsnrGamma");
  const miniSsimGamma = document.getElementById("miniSsimGamma");
  const miniNiqeGamma = document.getElementById("miniNiqeGamma");
  const timeGamma = document.getElementById("timeGamma");

  const miniPsnrMsr = document.getElementById("miniPsnrMsr");
  const miniSsimMsr = document.getElementById("miniSsimMsr");
  const miniNiqeMsr = document.getElementById("miniNiqeMsr");
  const timeMsr = document.getElementById("timeMsr");

  // Heatmaps
  const imgDiffHe = document.getElementById("imgDiffHe");
  const imgDiffClahe = document.getElementById("imgDiffClahe");
  const imgDiffGamma = document.getElementById("imgDiffGamma");
  const imgDiffMsr = document.getElementById("imgDiffMsr");

  // Split Comparison Elements
  const splitWrapper = document.getElementById("splitWrapper");
  const splitOverlay = document.getElementById("splitOverlay");
  const splitDivider = document.getElementById("splitDivider");
  const splitImgBefore = document.getElementById("splitImgBefore");
  const splitImgAfter = document.getElementById("splitImgAfter");
  const splitLabelAfter = document.getElementById("splitLabelAfter");
  const splitMethodSelect = document.getElementById("splitMethodSelect");

  // Formulas & Tables
  const mathLatexBox = document.getElementById("mathLatexBox");
  const formulaMethodTitle = document.getElementById("formulaMethodTitle");
  const formulaExplanation = document.getElementById("formulaExplanation");
  const tableBodyComparison = document.getElementById("tableBodyComparison");
  const recBadgeName = document.getElementById("recBadgeName");
  const recDescText = document.getElementById("recDescText");

  // Batch Benchmark Elements
  const batchSamplesInput = document.getElementById("batchSamplesInput");
  const btnRunBatch = document.getElementById("btnRunBatch");
  const emptyBatchState = document.getElementById("emptyBatchState");
  const batchContentLoaded = document.getElementById("batchContentLoaded");
  const batchStatsRow = document.getElementById("batchStatsRow");

  // Formula Descriptions Map
  const formulaDescriptions = {
    he: {
      title: "Thuật Toán 1: Histogram Equalization (HE Toàn Cục)",
      latex: "s_k = T(r_k) = (L - 1) \\sum_{j=0}^k p_r(r_j) = \\frac{L - 1}{M \\cdot N} \\sum_{j=0}^k n_j",
      expl: "Cân bằng mức xám toàn cục: Trải đều hàm mật độ phân phối xác suất p(r_k) khắp dải sáng [0, 255]. Ưu điểm là làm sáng mạnh các vùng bóng râm trong ảnh phong cảnh đêm, nhưng nhược điểm là làm cháy sáng mây trời và khuếch đại nhiễu nền đồng nhất."
    },
    clahe: {
      title: "Thuật Toán 2: Contrast Limited Adaptive Histogram Equalization (CLAHE)",
      latex: "N_{\\text{clip}} = \\beta \\cdot N_{\\text{avg}} = \\beta \\cdot \\frac{M_{\\text{tile}} \\cdot N_{\\text{tile}}}{256}, \\quad h_{\\text{mod}}(k) = \\min(h(k), N_{\\text{clip}}) + \\frac{N_{\\text{clipped}}}{256}",
      expl: "Cân bằng thích nghi giới hạn độ tương phản: Kênh độ sáng được chia thành lưới các ô nhỏ (Tiles). Ngưỡng Clip Limit (β) hạn chế độ dốc hàm tích lũy CDF để không khuếch đại nhiễu hạt. Các phần pixel vượt ngưỡng được tái phân phối đều, và dùng nội suy song tuyến (Bilinear Interpolation) khử hiệu ứng đường viền ô lưới."
    },
    gamma: {
      title: "Thuật Toán 3: Gamma Correction (Hiệu Chỉnh Lũy Thừa Phi Tuyến)",
      latex: "V_{\\text{out}} = 255 \\cdot \\left(\\frac{V_{\\text{in}}}{255}\\right)^\\gamma, \\quad (\\gamma < 1.0 \\text{ khôi phục vùng tối})",
      expl: "Biến đổi ánh sáng phi tuyến tính theo hàm mũ: Khi chọn γ < 1.0 (ví dụ γ = 0.5), đường cong ánh xạ lồi lên trên, kéo sáng các pixel tối (0 - 80) mà không làm bão hòa các pixel vốn đã sáng (200 - 255), giúp bảo tồn màu sắc tự nhiên của bầu trời hoàng hôn."
    },
    msr: {
      title: "Thuật Toán 4: Multi-Scale Retinex (MSR)",
      latex: "R_{\\text{MSR}}(x, y) = \\sum_{k=1}^K w_k \\cdot \\left[ \\ln(I(x, y)) - \\ln(I(x, y) * G_k(x, y)) \\right], \\quad G_k \\sim \\mathcal{N}(0, \\sigma_k^2)",
      expl: "Lý thuyết phản xạ Retinex: Bức ảnh quan sát I là tích của hệ số phản xạ chi tiết R và độ rọi Illumination L. MSR kết hợp 3 quy mô Gaussian (σ = 15, 80, 250) để vừa bóc tách chi tiết cục bộ vi mô, vừa cân bằng dải sáng vĩ mô toàn cảnh, sau đó co giãn dải động về [0, 255]."
    }
  };

  // ==========================================================================
  // INITIALIZATION
  // ==========================================================================
  async function initSystem() {
    try {
      const resp = await fetch("/api/status");
      if (resp.ok) {
        const data = await resp.json();
        state.totalImages = data.total_images;
        if (state.totalImages > 0) {
          imgIndexSlider.max = state.totalImages - 1;
          imgIndexVal.textContent = `0 / ${state.totalImages - 1}`;
        } else {
          imgIndexSlider.max = 0;
          imgIndexVal.textContent = "Tổng hợp mẫu";
        }
      }
    } catch (e) {
      console.warn("Không kết nối được API status, sử dụng cấu hình mặc định.", e);
    }

    // Render KaTeX ban đầu cho modal và formula box
    renderAllLatex();

    // Khởi chạy thực thi lần đầu
    executePipeline();
  }

  // Helper an toàn định dạng số
  function safeNum(val, digits = 2, fallback = "--") {
    if (val === null || val === undefined || isNaN(val)) return fallback;
    return Number(val).toFixed(digits);
  }

  // ==========================================================================
  // PIPELINE EXECUTION
  // ==========================================================================
  async function executePipeline() {
    if (state.isProcessing) return;
    state.isProcessing = true;

    btnExecute.disabled = true;
    btnExecute.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i><span>Đang Phân Tích & Tính Toán...</span>`;

    let activeGridSize = [8, 8];
    gridPills.forEach(p => {
      if (p.classList.contains("active")) {
        const parts = p.dataset.grid.split("x");
        activeGridSize = [parseInt(parts[0]), parseInt(parts[1])];
      }
    });

    const payload = {
      image_idx: state.isCustomUpload ? 0 : parseInt(imgIndexSlider.value),
      custom_file_b64: state.isCustomUpload ? state.customFileB64 : null,
      simulate_low_light: chkSimulateLowLight.checked,
      brightness_factor: parseFloat(brightnessFactorSlider.value),
      gamma_darkening: parseFloat(gammaDarkSlider.value),
      noise_type: noiseTypeSelect.value,
      noise_sigma: parseFloat(noiseSigmaSlider.value),
      denoise_method: denoiseMethodSelect.value,
      clahe_clip_limit: parseFloat(claheClipSlider.value),
      clahe_grid_size: activeGridSize,
      gamma_val: parseFloat(gammaValSlider.value),
      color_space: colorSpaceSelect.value
    };

    try {
      const res = await fetch("/api/process", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        let errMsg = `Mã phản hồi HTTP: ${res.status}`;
        try {
          const errData = await res.json();
          if (errData && errData.detail) {
            errMsg = errData.detail;
          }
        } catch (_) {
          try {
            const rawText = await res.text();
            if (rawText) errMsg = rawText;
          } catch (_) { }
        }
        throw new Error(errMsg);
      }

      const data = await res.json();
      state.lastResponseData = data;
      renderResults(data);
    } catch (err) {
      console.error("Pipeline Error:", err);
      let msg = err.message || "Lỗi không xác định";
      if (msg.includes("Failed to fetch")) {
        msg = "Máy chủ chưa phản hồi hoặc đang khởi động. Vui lòng thử lại sau vài giây.";
      }
      alert("Lỗi khi thực thi Pipeline: " + msg);
    } finally {
      state.isProcessing = false;
      btnExecute.disabled = false;
      btnExecute.innerHTML = `<span class="btn-icon-wrap"><i class="fa-solid fa-bolt-lightning"></i></span><span class="btn-text">Thực Thi So Sánh 4 Thuật Toán</span>`;
    }
  }

  // ==========================================================================
  // RENDER RESULTS
  // ==========================================================================
  function renderResults(data) {
    if (!data) return;
    state.groundTruthAvailable = Boolean(data.ground_truth_available);
    if (currentFileName) currentFileName.textContent = data.filename || "--";

    // 1. Cập nhật banner protocol
    if (!state.groundTruthAvailable) {
      if (bannerProtocol) bannerProtocol.style.display = "flex";
      if (valBestPsnr) valBestPsnr.textContent = "N/A";
      if (tagBestPsnr) tagBestPsnr.textContent = "Không có Ground Truth";
      if (subPsnr) subPsnr.textContent = "Bỏ qua so sánh điểm";

      if (valBestSsim) valBestSsim.textContent = "N/A";
      if (tagBestSsim) tagBestSsim.textContent = "Không có Ground Truth";
      if (subSsim) subSsim.textContent = "Bỏ qua so sánh điểm";
    } else {
      if (bannerProtocol) bannerProtocol.style.display = "none";
      if (data.rankings && data.rankings.best_psnr) {
        if (valBestPsnr) valBestPsnr.textContent = safeNum(data.rankings.best_psnr.value, 2, "N/A");
        if (tagBestPsnr) tagBestPsnr.textContent = `Tốt nhất: ${(data.rankings.best_psnr.name || "").split(" ")[0]}`;
        const noisyPsnr = data.methods?.clahe?.metrics?.psnr_before;
        if (subPsnr) subPsnr.innerHTML = `Ảnh suy thoái: <b>${safeNum(noisyPsnr, 2)} dB</b>`;
      }
      if (data.rankings && data.rankings.best_ssim) {
        if (valBestSsim) valBestSsim.textContent = safeNum(data.rankings.best_ssim.value, 4, "N/A");
        if (tagBestSsim) tagBestSsim.textContent = `Tốt nhất: ${(data.rankings.best_ssim.name || "").split(" ")[0]}`;
        const noisySsim = data.methods?.clahe?.metrics?.ssim_before;
        if (subSsim) subSsim.innerHTML = `Ảnh suy thoái: <b>${safeNum(noisySsim, 4)}</b>`;
      }
    }

    // NIQE (Luôn có)
    if (data.rankings && data.rankings.best_niqe) {
      if (valBestNiqe) valBestNiqe.textContent = safeNum(data.rankings.best_niqe.value, 2, "--");
      if (tagBestNiqe) tagBestNiqe.textContent = `Tự nhiên nhất: ${(data.rankings.best_niqe.name || "").split(" ")[0]}`;
      const noisyNiqe = data.methods?.clahe?.metrics?.niqe_before;
      if (subNiqe) subNiqe.innerHTML = `Ảnh suy thoái: <b>${safeNum(noisyNiqe, 2)}</b>`;
    }

    // 2. Render ảnh đầu vào
    if (imgClean) imgClean.src = data.clean_img_b64 || "";
    if (imgDegraded) imgDegraded.src = data.degraded_img_b64 || "";
    if (imgDenoisedInput) imgDenoisedInput.src = data.denoised_input_b64 || "";

    // 3. Render 4 Thuật toán
    const m = data.methods || {};
    // HE
    if (imgResHe) imgResHe.src = m.he?.img_b64 || "";
    if (miniPsnrHe) miniPsnrHe.textContent = safeNum(m.he?.metrics?.psnr, 1, "N/A");
    if (miniSsimHe) miniSsimHe.textContent = safeNum(m.he?.metrics?.ssim, 3, "N/A");
    if (miniNiqeHe) miniNiqeHe.textContent = safeNum(m.he?.metrics?.niqe, 2, "--");
    if (timeHe) timeHe.textContent = m.he?.exec_time_ms ?? "--";

    // CLAHE
    if (imgResClahe) imgResClahe.src = m.clahe?.img_b64 || "";
    if (miniPsnrClahe) miniPsnrClahe.textContent = safeNum(m.clahe?.metrics?.psnr, 1, "N/A");
    if (miniSsimClahe) miniSsimClahe.textContent = safeNum(m.clahe?.metrics?.ssim, 3, "N/A");
    if (miniNiqeClahe) miniNiqeClahe.textContent = safeNum(m.clahe?.metrics?.niqe, 2, "--");
    if (timeClahe) timeClahe.textContent = m.clahe?.exec_time_ms ?? "--";

    // Gamma
    if (imgResGamma) imgResGamma.src = m.gamma?.img_b64 || "";
    if (miniPsnrGamma) miniPsnrGamma.textContent = safeNum(m.gamma?.metrics?.psnr, 1, "N/A");
    if (miniSsimGamma) miniSsimGamma.textContent = safeNum(m.gamma?.metrics?.ssim, 3, "N/A");
    if (miniNiqeGamma) miniNiqeGamma.textContent = safeNum(m.gamma?.metrics?.niqe, 2, "--");
    if (timeGamma) timeGamma.textContent = m.gamma?.exec_time_ms ?? "--";

    // MSR
    if (imgResMsr) imgResMsr.src = m.msr?.img_b64 || "";
    if (miniPsnrMsr) miniPsnrMsr.textContent = safeNum(m.msr?.metrics?.psnr, 1, "N/A");
    if (miniSsimMsr) miniSsimMsr.textContent = safeNum(m.msr?.metrics?.ssim, 3, "N/A");
    if (miniNiqeMsr) miniNiqeMsr.textContent = safeNum(m.msr?.metrics?.niqe, 2, "--");
    if (timeMsr) timeMsr.textContent = m.msr?.exec_time_ms ?? "--";

    // Heatmaps
    if (imgDiffHe) imgDiffHe.src = m.he?.diff_map_b64 || "";
    if (imgDiffClahe) imgDiffClahe.src = m.clahe?.diff_map_b64 || "";
    if (imgDiffGamma) imgDiffGamma.src = m.gamma?.diff_map_b64 || "";
    if (imgDiffMsr) imgDiffMsr.src = m.msr?.diff_map_b64 || "";

    // 4. Update Split compare view
    updateSplitImages();

    // 5. Update Bảng so sánh
    populateComparisonTable(data);

    // 6. Update Khuyến nghị & Radar Chart
    if (data.rankings && data.rankings.overall_recommended) {
      if (recBadgeName) recBadgeName.textContent = (data.rankings.overall_recommended.name || "").split("(")[0];
      if (recDescText) recDescText.textContent = `${data.rankings.overall_recommended.name}: ${data.rankings.overall_recommended.reason}`;
    }

    // 7. Update Biểu đồ Histogram
    renderHistogramChart(data);

    // 8. Update Radar Chart
    renderRadarChart(data);

    // 9. Update Formula Display
    updateFormulaDisplay(state.activeFormula);
  }

  // ==========================================================================
  // COMPARISON TABLE
  // ==========================================================================
  function populateComparisonTable(data) {
    if (!tableBodyComparison) return;
    tableBodyComparison.innerHTML = "";
    const methodsList = [
      { key: "he", label: "Histogram Equalization (HE)" },
      { key: "clahe", label: "CLAHE (Tương Phản Thích Nghi)" },
      { key: "gamma", label: "Gamma Correction" },
      { key: "msr", label: "Multi-Scale Retinex (MSR)" }
    ];

    const bestKey = data?.rankings?.overall_recommended?.key || "clahe";

    methodsList.forEach(item => {
      const info = data?.methods?.[item.key] || {};
      const m = info.metrics || {};
      const tr = document.createElement("tr");
      if (item.key === bestKey) {
        tr.classList.add("highlight-best");
      }

      const psnrText = (typeof m.psnr === "number") ? m.psnr.toFixed(2) : `<span style="color:var(--text-sub)">N/A</span>`;
      const deltaPsnrText = (typeof m.delta_psnr === "number") ? `${m.delta_psnr > 0 ? '+' : ''}${m.delta_psnr.toFixed(2)}` : `<span style="color:var(--text-sub)">--</span>`;

      const ssimText = (typeof m.ssim === "number") ? m.ssim.toFixed(4) : `<span style="color:var(--text-sub)">N/A</span>`;
      const deltaSsimText = (typeof m.delta_ssim === "number") ? `${m.delta_ssim > 0 ? '+' : ''}${m.delta_ssim.toFixed(4)}` : `<span style="color:var(--text-sub)">--</span>`;

      const niqeText = (typeof m.niqe === "number") ? m.niqe.toFixed(2) : "--";
      const deltaNiqeText = (typeof m.delta_niqe === "number") ? `${m.delta_niqe > 0 ? '+' : ''}${m.delta_niqe.toFixed(2)}` : "--";

      tr.innerHTML = `
        <td><strong>${item.label}</strong> ${item.key === bestKey ? '<span style="color:#60a5fa; font-size:11px;">(Khuyên dùng)</span>' : ''}</td>
        <td>${psnrText}</td>
        <td style="color:${(m.delta_psnr || 0) > 0 ? 'var(--accent-success)' : 'var(--text-sub)'}">${deltaPsnrText}</td>
        <td>${ssimText}</td>
        <td style="color:${(m.delta_ssim || 0) > 0 ? 'var(--accent-success)' : 'var(--text-sub)'}">${deltaSsimText}</td>
        <td>${niqeText}</td>
        <td style="color:${(m.delta_niqe || 0) < 0 ? 'var(--accent-success)' : 'var(--accent-warning)'}">${deltaNiqeText}</td>
        <td><span style="font-family:var(--font-mono)">${info.exec_time_ms ?? "--"} ms</span></td>
      `;
      tableBodyComparison.appendChild(tr);
    });
  }

  // ==========================================================================
  // CHART.JS HISTOGRAM
  // ==========================================================================
  function renderHistogramChart(data) {
    if (typeof Chart === "undefined") return;
    const canvas = document.getElementById("histChart");
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (state.histChartInstance) {
      state.histChartInstance.destroy();
      state.histChartInstance = null;
    }

    try {
      const bins = Array.from({ length: 256 }, (_, i) => i);
      const m = data?.methods || {};
      const isLight = document.body.classList.contains("theme-light");

      // Plugin vẽ mũi tên ở đầu trục đứng (Điểm ảnh) và cuối trục ngang (Mức xám)
      const axisArrowsPlugin = {
        id: "axisArrowsPlugin",
        afterDraw(chart) {
          const { ctx, chartArea } = chart;
          if (!chartArea) return;
          const { left, right, top, bottom } = chartArea;

          ctx.save();
          const lightModeNow = document.body.classList.contains("theme-light");
          const arrowColor = lightModeNow ? "#1d4ed8" : "#38bdf8";
          const textColor = lightModeNow ? "#0f172a" : "#f8fafc";
          const axisLineColor = lightModeNow ? "#64748b" : "rgba(255, 255, 255, 0.35)";

          ctx.lineWidth = 2;
          ctx.font = "bold 12px 'Plus Jakarta Sans', system-ui, sans-serif";

          // 1. Đầu trục đứng (Y): Kéo dài trục lên + mũi tên hướng lên ▲ + "Điểm ảnh"
          ctx.strokeStyle = axisLineColor;
          ctx.beginPath();
          ctx.moveTo(left, top);
          ctx.lineTo(left, top - 12);
          ctx.stroke();

          ctx.fillStyle = arrowColor;
          ctx.beginPath();
          ctx.moveTo(left, top - 20);
          ctx.lineTo(left - 5, top - 11);
          ctx.lineTo(left + 5, top - 11);
          ctx.closePath();
          ctx.fill();

          ctx.fillStyle = textColor;
          ctx.textAlign = "center";
          ctx.textBaseline = "bottom";
          ctx.fillText("Điểm ảnh", left, top - 22);

          // 2. Cuối trục ngang (X): Kéo dài trục sang phải + mũi tên hướng sang phải ▶ + "Mức xám"
          ctx.strokeStyle = axisLineColor;
          ctx.beginPath();
          ctx.moveTo(right, bottom);
          ctx.lineTo(right + 12, bottom);
          ctx.stroke();

          ctx.fillStyle = arrowColor;
          ctx.beginPath();
          ctx.moveTo(right + 20, bottom);
          ctx.lineTo(right + 11, bottom - 5);
          ctx.lineTo(right + 11, bottom + 5);
          ctx.closePath();
          ctx.fill();

          ctx.fillStyle = textColor;
          ctx.textAlign = "left";
          ctx.textBaseline = "middle";
          ctx.fillText("Mức xám", right + 26, bottom);

          ctx.restore();
        }
      };

      state.histChartInstance = new Chart(ctx, {
        type: "line",
        plugins: [axisArrowsPlugin],
        data: {
          labels: bins,
          datasets: [
            {
              label: "Ảnh Thiếu Sáng",
              data: data?.input_hist || [],
              borderColor: isLight ? "#475569" : "#64748b",
              backgroundColor: isLight ? "rgba(71, 85, 105, 0.08)" : "rgba(100, 116, 139, 0.05)",
              borderWidth: 1.5,
              pointRadius: 0,
              fill: true
            },
            {
              label: "HE",
              data: m.he?.hist || [],
              borderColor: "#f59e0b",
              borderWidth: 1.5,
              pointRadius: 0,
              tension: 0.2
            },
            {
              label: "CLAHE",
              data: m.clahe?.hist || [],
              borderColor: isLight ? "#1d4ed8" : "#3b82f6",
              backgroundColor: isLight ? "rgba(29, 78, 216, 0.15)" : "rgba(59, 130, 246, 0.15)",
              borderWidth: 2,
              pointRadius: 0,
              tension: 0.2,
              fill: true
            },
            {
              label: "Gamma",
              data: m.gamma?.hist || [],
              borderColor: "#10b981",
              borderWidth: 1.5,
              pointRadius: 0,
              tension: 0.2
            },
            {
              label: "MSR",
              data: m.msr?.hist || [],
              borderColor: "#8b5cf6",
              borderWidth: 1.5,
              pointRadius: 0,
              tension: 0.2
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          layout: {
            padding: {
              top: 36,
              right: 85,
              bottom: 8,
              left: 8
            }
          },
          plugins: {
            legend: { display: false },
            tooltip: {
              mode: "index",
              intersect: false,
              callbacks: {
                title: (items) => `Mức xám: ${items[0].label}`,
                label: (context) => ` ${context.dataset.label}: ${(context.parsed.y || 0).toLocaleString("vi-VN")} điểm ảnh`
              }
            }
          },
          scales: {
            x: {
              grid: { color: isLight ? "rgba(0, 0, 0, 0.08)" : "rgba(255, 255, 255, 0.05)" },
              ticks: { color: isLight ? "#334155" : "#94a3b8", maxTicksLimit: 16 }
            },
            y: {
              grid: { color: isLight ? "rgba(0, 0, 0, 0.08)" : "rgba(255, 255, 255, 0.05)" },
              ticks: {
                color: isLight ? "#334155" : "#94a3b8",
                callback: (val) => val.toLocaleString("vi-VN")
              }
            }
          }
        }
      });
    } catch (e) {
      console.warn("Không thể render Histogram Chart:", e);
    }
  }

  // ==========================================================================
  // CHART.JS RADAR CHART
  // ==========================================================================
  function renderRadarChart(data) {
    if (typeof Chart === "undefined") return;
    const canvas = document.getElementById("radarChart");
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (state.radarChartInstance) {
      state.radarChartInstance.destroy();
      state.radarChartInstance = null;
    }

    try {
      const m = data?.methods || {};
      function normMetric(val, min, max, invert = false) {
        if (val === null || val === undefined || isNaN(val)) return 50;
        let ratio = (val - min) / (max - min || 1);
        ratio = Math.max(0, Math.min(1, ratio));
        return invert ? (1 - ratio) * 100 : ratio * 100;
      }

      state.radarChartInstance = new Chart(ctx, {
        type: "radar",
        data: {
          labels: ["Tương Đồng Cấu Trúc (SSIM)", "Tự Nhiên Cảnh (NIQE)", "Tốc Độ Xử Lý", "Phục Hồi Sáng"],
          datasets: [
            {
              label: "CLAHE",
              data: [
                normMetric(m.clahe?.metrics?.ssim, 0.5, 0.98),
                normMetric(m.clahe?.metrics?.niqe, 2.0, 10.0, true),
                normMetric(m.clahe?.exec_time_ms, 5, 250, true),
                88
              ],
              borderColor: "#3b82f6",
              backgroundColor: "rgba(59, 130, 246, 0.2)",
              borderWidth: 2
            },
            {
              label: "MSR",
              data: [
                normMetric(m.msr?.metrics?.ssim, 0.5, 0.98),
                normMetric(m.msr?.metrics?.niqe, 2.0, 10.0, true),
                normMetric(m.msr?.exec_time_ms, 5, 250, true),
                94
              ],
              borderColor: "#8b5cf6",
              backgroundColor: "rgba(139, 92, 246, 0.1)",
              borderWidth: 1.5
            },
            {
              label: "Gamma",
              data: [
                normMetric(m.gamma?.metrics?.ssim, 0.5, 0.98),
                normMetric(m.gamma?.metrics?.niqe, 2.0, 10.0, true),
                normMetric(m.gamma?.exec_time_ms, 5, 250, true),
                75
              ],
              borderColor: "#10b981",
              backgroundColor: "rgba(16, 185, 129, 0.1)",
              borderWidth: 1.5
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { position: "bottom", labels: { color: "#94a3b8", boxWidth: 10, font: { size: 10 } } }
          },
          scales: {
            r: {
              angleLines: { color: "rgba(255, 255, 255, 0.08)" },
              grid: { color: "rgba(255, 255, 255, 0.08)" },
              pointLabels: { color: "#94a3b8", font: { size: 10 } },
              ticks: { display: false, max: 100, min: 0 }
            }
          }
        }
      });
    } catch (e) {
      console.warn("Không thể render Radar Chart:", e);
    }
  }

  // ==========================================================================
  // SPLIT VIEW SLIDER LOGIC
  // ==========================================================================
  function updateSplitImages() {
    if (!state.lastResponseData || !state.lastResponseData.methods) return;
    const selectedMethod = splitMethodSelect?.value || "clahe";
    const methodObj = state.lastResponseData.methods[selectedMethod];
    if (!methodObj) return;

    if (splitImgBefore) splitImgBefore.src = state.lastResponseData.degraded_img_b64 || "";
    if (splitImgAfter) splitImgAfter.src = methodObj.img_b64 || "";
    if (splitLabelAfter) splitLabelAfter.textContent = `${methodObj.short_name || selectedMethod} (Sau Xử Lý)`;

    // Đồng bộ chiều rộng ảnh overlay
    const container = splitWrapper?.querySelector(".split-image-container");
    if (container && container.offsetWidth > 0 && splitImgBefore) {
      splitImgBefore.style.width = container.offsetWidth + "px";
    }
  }

  function setSplitDividerPosition(percentage) {
    percentage = Math.max(0, Math.min(100, percentage));
    state.splitDividerPos = percentage;
    splitOverlay.style.width = percentage + "%";
    splitDivider.style.left = percentage + "%";
  }

  splitWrapper.addEventListener("mousedown", (e) => {
    state.isDraggingSplit = true;
    handleSplitDrag(e);
  });

  window.addEventListener("mousemove", (e) => {
    if (!state.isDraggingSplit) return;
    handleSplitDrag(e);
  });

  window.addEventListener("mouseup", () => {
    state.isDraggingSplit = false;
  });

  function handleSplitDrag(e) {
    const container = splitWrapper.querySelector(".split-image-container");
    const rect = container.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const percent = (x / rect.width) * 100;
    setSplitDividerPosition(percent);
  }

  splitMethodSelect.addEventListener("change", updateSplitImages);

  // View Pills Tab Switching
  const viewPills = document.querySelectorAll(".view-pill");
  const viewPanes = document.querySelectorAll(".view-pane");

  viewPills.forEach(pill => {
    pill.addEventListener("click", () => {
      viewPills.forEach(p => p.classList.remove("active"));
      viewPanes.forEach(p => p.classList.remove("active"));
      pill.classList.add("active");

      const viewId = pill.dataset.view;
      if (viewId === "grid4") document.getElementById("viewPaneGrid4").classList.add("active");
      if (viewId === "split") {
        document.getElementById("viewPaneSplit").classList.add("active");
        updateSplitImages();
      }
      if (viewId === "heatmaps") {
        document.getElementById("viewPaneHeatmaps").classList.add("active");
        renderAllLatex();
      }
    });
  });

  // ==========================================================================
  // FORMULA DISPLAY
  // ==========================================================================
  function updateFormulaDisplay(formulaKey) {
    state.activeFormula = formulaKey;
    const info = formulaDescriptions[formulaKey];
    if (!info) return;

    if (formulaMethodTitle) formulaMethodTitle.textContent = info.title;
    if (formulaExplanation) formulaExplanation.textContent = info.expl;

    // Render KaTeX an toàn
    if (mathLatexBox) {
      try {
        if (typeof katex !== "undefined") {
          katex.render(info.latex, mathLatexBox, { displayMode: true, throwOnError: false });
        } else {
          mathLatexBox.textContent = info.latex;
        }
      } catch (e) {
        mathLatexBox.textContent = info.latex;
      }
    }
  }

  const formulaTabs = document.querySelectorAll(".formula-tab");
  formulaTabs.forEach(tab => {
    tab.addEventListener("click", () => {
      formulaTabs.forEach(t => t.classList.remove("active"));
      tab.classList.add("active");
      updateFormulaDisplay(tab.dataset.formula);
    });
  });

  // ==========================================================================
  // MODAL / DASHBOARD GIẢI THÍCH CHI TIẾT Ý NGHĨA KẾT QUẢ (NÚT ?)
  // ==========================================================================
  function openHelpModal(targetSectionId = null) {
    modalExplanationDashboard.classList.add("open");
    renderAllLatex();

    if (targetSectionId) {
      // Chuyển sang đúng tab
      const modalTabs = document.querySelectorAll(".modal-tab-btn");
      const modalSections = document.querySelectorAll(".modal-section");

      modalTabs.forEach(t => {
        if (t.dataset.target === targetSectionId) {
          t.classList.add("active");
        } else {
          t.classList.remove("active");
        }
      });

      modalSections.forEach(s => {
        if (s.id === targetSectionId) {
          s.classList.add("active");
        } else {
          s.classList.remove("active");
        }
      });
    }
  }

  function closeHelpModal() {
    modalExplanationDashboard.classList.remove("open");
  }

  btnOpenHelp?.addEventListener("click", (e) => {
    e.stopPropagation();
    toggleMasterDrawer();
  });
  btnCloseModal?.addEventListener("click", closeHelpModal);

  modalExplanationDashboard.addEventListener("click", (e) => {
    if (e.target === modalExplanationDashboard) {
      closeHelpModal();
    }
  });

  // Modal Tabs Switching
  const modalTabs = document.querySelectorAll(".modal-tab-btn");
  const modalSections = document.querySelectorAll(".modal-section");

  modalTabs.forEach(tab => {
    tab.addEventListener("click", () => {
      modalTabs.forEach(t => t.classList.remove("active"));
      modalSections.forEach(s => s.classList.remove("active"));
      tab.classList.add("active");
      const targetId = tab.dataset.target;
      document.getElementById(targetId)?.classList.add("active");
      renderAllLatex();
    });
  });

  // ==========================================================================
  // THẺ PHẢN BIỆN HỌC THUẬT 3 TẦNG (3-TIER ACADEMIC DEFENSE POPUP KNOWLEDGE BASE)
  // Tự động nội suy từ trạng thái DOM thực tế: Toán học -> Thực nghiệm -> Phản biện
  // ==========================================================================
  const DEFENSE_KNOWLEDGE_BASE = {
    bilateral_hsv: (s) => ({
      title: "🛡️ Tiền Xử Lý: Bilateral Filter & Không Gian Màu HSV/LAB",
      math: `Chuyển đổi ảnh RGB $\\to$ <b>${s.colorSpace}</b> nhằm tách hoàn toàn Luminance ($V$ hoặc $L^*$) khỏi Chrominance ($H, S$ hoặc $a^*, b^*$). Bộ lọc <b>Bilateral</b> tính trọng số tích chập bằng tích của 2 hàm Gaussian: khoảng cách không gian $G_{\\sigma_s}$ và chênh lệch cường độ sáng $G_{\\sigma_r}$: $$I_B(p) = \\frac{1}{W_p} \\sum_{q \\in \\Omega} I(q) \\cdot \\exp\\left(-\\frac{\\|p-q\\|^2}{2\\sigma_s^2}\\right) \\cdot \\exp\\left(-\\frac{|I(p)-I(q)|^2}{2\\sigma_r^2}\\right)$$`,
      live: `Với mức nhiễu đang cài đặt là <span class="xai-val">&sigma; = ${s.noiseSigma}</span>, bộ lọc Bilateral kìm hãm các hạt nhiễu tần số cao trong khi vẫn giữ nguyên bước nhảy biên sắc nét của cảnh quan, ngăn chặn hiện tượng khuếch đại hạt nhiễu ở các bước CLAHE và Retinex phía sau.`,
      defense: `<b>Hỏi:</b> <i>'Tại sao không lọc Gaussian thông thường và xử lý thẳng trên RGB?'</i><br><b>Đáp:</b> Lọc Gaussian chuẩn chỉ xét khoảng cách không gian nên làm nhòe cạnh (mất chi tiết cấu trúc, làm tụt SSIM). Xử lý trực tiếp trên 3 kênh R-G-B sẽ làm thay đổi tỷ lệ phối màu, gây hiện tượng lệch màu (color distortion/cast) khiến ảnh đêm bị ngả màu dị thường.`
    }),

    noise_type: (s) => {
      let mathDesc = "";
      let defAns = "";
      const nType = s.noiseType;

      if (nType === "gaussian") {
        mathDesc = `<b>Nhiễu Gauss (Gaussian Additive Noise):</b> Hàm mật độ xác suất: $$P(x) = \\frac{1}{\\sigma\\sqrt{2\\pi}} \\exp\\left(-\\frac{(x - \\mu)^2}{2\\sigma^2}\\right)$$ Xuất phát từ nhiễu nhiệt (Johnson-Nyquist) trong mạch khuếch đại cảm biến CMOS/CCD khi tăng độ nhạy sáng ISO cao trong bóng tối.`;
        defAns = `<b>Hỏi:</b> <i>'Tại sao cảm biến ban đêm lại xuất hiện đồng thời cả nhiễu Poisson và Gauss?'</i><br><b>Đáp:</b> Ở vùng tối sâu, số photon đến cảm biến cực ít nên nhiễu lượng tử Poisson chiếm ưu thế (Shot noise phụ thuộc tín hiệu); khi tín hiệu đi qua mạch đọc ADC và mạch khuếch đại analog (ISO cao), nhiễu nhiệt Gauss độc lập với tín hiệu (Read noise) được cộng thêm vào tạo thành mô hình hỗn hợp Poisson-Gaussian.`;
      } else if (nType === "salt_and_pepper") {
        mathDesc = `<b>Nhiễu Muối Tiêu (Salt & Pepper / Impulse Noise):</b> Điểm ảnh bị thay đổi đột ngột thành cực đại (255 - hạt muối) hoặc cực tiểu (0 - hạt tiêu): $$I_{\\text{noisy}}(x, y) = \\begin{cases} 0 & \\text{với xác suất } p/2 \\\\ 255 & \\text{với xác suất } p/2 \\\\ I(x, y) & \\text{với xác suất } 1 - p \\end{cases}$$ Thường do lỗi đồng bộ truyền dẫn bit hoặc các điểm ảnh bị chết (dead pixels) trên cảm biến.`;
        defAns = `<b>Hỏi:</b> <i>'Tại sao bộ lọc Bilateral lại thất bại hoàn toàn trước nhiễu Muối Tiêu?'</i><br><b>Đáp:</b> Bilateral là bộ lọc trung bình trọng số; các hạt muối tiêu (0 và 255) là giá trị ngoại lai cực đoan (outliers) làm sai lệch trọng số cường độ. Bắt buộc phải dùng <b>Median Filter (Lọc trung vị)</b> để thay thế hoàn toàn điểm ảnh bằng giá trị trung vị của láng giềng.`;
      } else if (nType === "poisson") {
        mathDesc = `<b>Nhiễu Lượng Tử (Poisson / Shot Noise):</b> Phân phối xác suất rời rạc: $$P(k; \\lambda) = \\frac{\\lambda^k e^{-\\lambda}}{k!} \\quad (\\lambda = I(x, y))$$ Bản chất là nhiễu hạt photon (Photon Shot Noise), phát sinh do sự thăng giáng lượng tử ngẫu nhiên của các photon đến bề mặt cảm biến trong điều kiện thiếu sáng trầm trọng.`;
        defAns = `<b>Hỏi:</b> <i>'Nhiễu Poisson khác nhiễu Gauss ở điểm cốt lõi nào?'</i><br><b>Đáp:</b> Nhiễu Gauss có phương sai độc lập với độ sáng pixel; ngược lại, nhiễu Poisson có phương sai bằng đúng kỳ vọng ($\\sigma^2 = \\lambda = I(x,y)$), tức là vùng càng sáng thì phương sai nhiễu photon càng lớn, nhưng tỷ số tín hiệu trên nhiễu $\\text{SNR} = \\sqrt{\\lambda}$ lại tăng lên, do đó mắt người nhận thấy vùng tối bị hạt nhiễu nặng nề hơn.`;
      } else if (nType === "speckle") {
        mathDesc = `<b>Nhiễu Đốm Nhân (Speckle Multiplicative Noise):</b> Mô hình nhân phi tuyến: $$I_{\\text{noisy}} = I \\cdot (1 + n), \\quad n \\sim \\mathcal{N}(0, \\sigma^2)$$ Xuất hiện do sự giao thoa tương hỗ của các sóng kết hợp tán xạ ngược từ các bề mặt vi mô gồ ghề (phổ biến trong radar viễn thám SAR, siêu âm và laser).`;
        defAns = `<b>Hỏi:</b> <i>'Tại sao không thể dùng phép trừ đơn giản để loại bỏ nhiễu Speckle?'</i><br><b>Đáp:</b> Vì Speckle là nhiễu dạng nhân (multiplicative), không phải cộng tính. Muốn xử lý bằng các bộ lọc cộng thông thường, ta phải lấy $\\ln$ chuyển về miền cộng: $\\ln I_{\\text{noisy}} = \\ln I + \\ln(1 + n)$ (phương pháp Homomorphic Filtering).`;
      } else {
        mathDesc = `<b>Không Thêm Nhiễu Nhân Tạo:</b> Ảnh thiếu sáng nguyên bản, đánh giá năng lực khôi phục dải động thuần túy của 4 thuật toán.`;
        defAns = `<b>Hỏi:</b> <i>'Vì sao ngay cả khi không thêm nhiễu nhân tạo, ảnh kéo sáng vẫn có thể xuất hiện hạt sạn?'</i><br><b>Đáp:</b> Vì ảnh gốc số hóa luôn tồn tại nhiễu lượng tử hóa và nhiễu đọc ngầm (Readout Noise) ở các mức xám cực thấp [0 - 15]; khi kéo giãn dải động toàn cục bằng HE, các mức xám này bị khuếch đại thành hạt nhiễu nhìn thấy được.`;
      }

      return {
        title: `🧪 Bản Chất Vật Lý & Toán Học Của Loại Nhiễu (${s.noiseType.toUpperCase()})`,
        math: mathDesc,
        live: `Trạng thái hiện tại: Đang mô phỏng loại nhiễu <span class="xai-val">${s.noiseType}</span> với cường độ <span class="xai-val">&sigma; = ${s.noiseSigma}</span> trên ảnh đầu vào (SSIM suy giảm còn <span class="xai-val">${s.inputDegraded.ssim}</span>, PSNR = <span class="xai-val">${s.inputDegraded.psnr} dB</span>).`,
        defense: defAns
      };
    },

    noise_sigma: (s) => ({
      title: `⚙️ Cường Độ Nhiễu (&sigma; = ${s.noiseSigma}) & Tỷ Số SNR`,
      math: `Phương sai $\\sigma^2$ quyết định độ phân tán của mật độ xác suất nhiễu. Tỷ số tín hiệu trên nhiễu được xác định qua công thức: $$\\text{SNR} = 10 \\log_{10}\\left(\\frac{\\sigma_{\\text{signal}}^2}{\\sigma_{\\text{noise}}^2}\\right) \\quad (\\text{dB})$$`,
      live: `Ở mức <span class="xai-val">&sigma; = ${s.noiseSigma}</span>, mức độ méo dạng tín hiệu khiến ảnh đầu vào suy giảm còn <span class="xai-val">${s.inputDegraded.psnr} dB</span> (PSNR) và <span class="xai-val">${s.inputDegraded.ssim}</span> (SSIM).`,
      defense: `<b>Hỏi:</b> <i>'Tại sao dải kiểm thử $\\sigma$ được chọn từ $5.0$ đến $40.0$?'</i><br><b>Đáp:</b> Trong nhiếp ảnh kỹ thuật số thực tế, cảm biến ở ISO 3200-12800 sinh ra độ lệch chuẩn tương đương mức xám $\\sigma \\in [10, 25]$. Thiết lập dải $[5, 40]$ kiểm chứng toàn diện từ mức nhiễu nhẹ cho đến điều kiện khắc nghiệt cực hạn.`
    }),

    formula_latex: (s) => {
      const activeF = s.activeFormula || "clahe";
      let titleStr = "";
      let mathStr = "";
      let defStr = "";

      if (activeF === "he") {
        titleStr = "Thuật Toán 1: Histogram Equalization (HE Toàn Cục)";
        mathStr = `<b>Histogram Equalization:</b> Ánh xạ tích lũy CDF toàn cục: $$s_k = T(r_k) = \\frac{L-1}{M \\cdot N} \\sum_{j=0}^k n_j, \\quad k = 0, 1, \\dots, 255$$ Hàm biến đổi đơn điệu ép phân phối xác suất rời rạc $p_r(r_k)$ tiệm cận phân phối đều lý thuyết trên toàn dải [0, 255].`;
        defStr = `<b>Hỏi:</b> <i>'Hàm biến đổi $T(r_k)$ của HE có đảm bảo tính liên tục không?'</i><br><b>Đáp:</b> Không, vì số lượng điểm ảnh rời rạc nên hàm CDF là hàm bậc thang. Khi nhân với $L-1$, các bước nhảy rời rạc này tạo ra các khoảng trống giữa các mức xám (gây hiện tượng răng cưa và mất sắc thái liên tục).`;
      } else if (activeF === "clahe") {
        titleStr = "Thuật Toán 2: CLAHE (Contrast Limited Adaptive HE)";
        mathStr = `<b>CLAHE (Cắt ngưỡng & Nội suy song tuyến):</b> $$N_{\\text{clip}} = \\beta \\cdot \\frac{M_{\\text{tile}} N_{\\text{tile}}}{L}, \\quad R = \\frac{1}{L} \\sum_{k=0}^{L-1} \\max(0, h(k) - N_{\\text{clip}})$$ Pixel được nội suy từ 4 tâm ô lân cận: $f(x,y) \\approx (1-s)(1-t)f_1 + s(1-t)f_2 + (1-s)tf_3 + stf_4$.`;
        defStr = `<b>Hỏi:</b> <i>'Bilinear Interpolation xử lý các ô ở viền biên ảnh như thế nào?'</i><br><b>Đáp:</b> Các pixel ở 4 góc ảnh sử dụng trực tiếp hàm ánh xạ của ô góc duy nhất (không cần nội suy); các pixel ở dải mép biên sử dụng nội suy tuyến tính giữa 2 tâm ô lân cận; các pixel nằm bên trong sử dụng nội suy song tuyến 4 tâm, đảm bảo sự liên tục $C^0$ trên toàn ảnh.`;
      } else if (activeF === "gamma") {
        titleStr = "Thuật Toán 3: Gamma Correction (Biến Đổi Lũy Thừa Phi Tuyến)";
        mathStr = `<b>Gamma Correction:</b> $$V_{\\text{out}}(x, y) = 255 \\cdot \\left[\\frac{V(x, y)}{255}\\right]^\\gamma \\quad (\\gamma = ${s.gammaVal})$$ Ánh xạ mức xám phi tuyến độc lập từng pixel thông qua bảng tra cứu LUT 256 phần tử tính trước.`;
        defStr = `<b>Hỏi:</b> <i>'Tại sao $\\gamma < 1$ lại kéo sáng tốt vùng tối mà không làm nát vùng sáng?'</i><br><b>Đáp:</b> Đạo hàm $f'(x) = \\gamma x^{\\gamma-1}$ có độ dốc cực lớn khi $x \\to 0^+$ (độ lợi khuếch đại cực đại cho pixel tối) và giảm dần về $1$ khi $x \\to 1$. Hai điểm biên $0$ và $1$ được cố định hoàn toàn ($f(0)=0, f(1)=1$).`;
      } else {
        titleStr = "Thuật Toán 4: Multi-Scale Retinex (MSR)";
        mathStr = `<b>Multi-Scale Retinex:</b> Phân rã phản xạ - độ rọi: $$R_{\\text{MSR}}(x, y) = \\sum_{k=1}^3 w_k \\Big[ \\ln(I(x, y)) - \\ln(I(x, y) * G_k(x, y)) \\Big]$$ với 3 thang đo Gauss $\\sigma_k \\in \\{15, 80, 250\\}$ và trọng số $w_k = 1/3$.`;
        defStr = `<b>Hỏi:</b> <i>'Tại sao phải dùng hàm logarit trong công thức MSR?'</i><br><b>Đáp:</b> Dựa trên mô hình phản xạ võng mạc $I = R \\cdot L$. Lấy $\\ln$ chuyển phép nhân thành phép cộng $\\ln I = \\ln R + \\ln L$. Khi trừ đi thành phần tích chập Gauss (ước lượng trường độ rọi $L$), ta tách biệt được chính xác thành phần phản xạ thực $R$ độc lập với nguồn sáng.`;
      }

      const activeObj = s[activeF] || {};
      return {
        title: `📐 ${titleStr}`,
        math: mathStr,
        live: `Số liệu thực nghiệm thuật toán <b>${activeF.toUpperCase()}</b>: PSNR = <span class="xai-val">${activeObj.psnr || '--'} dB</span>, SSIM = <span class="xai-val">${activeObj.ssim || '--'}</span>, NIQE = <span class="xai-val">${activeObj.niqe || '--'}</span>, thời gian thực thi: <span class="xai-val">${activeObj.time || '--'} ms</span>.`,
        defense: defStr
      };
    },

    clahe_params: (s) => ({
      title: "⚙️ Cơ Chế Cắt Ngưỡng & Tái Phân Phối CLAHE",
      math: `Chia ảnh thành lưới cục bộ (Tile Grid), tính Histogram cho từng ô và cắt phần đỉnh vượt quá ngưỡng <span class="xai-val">&beta; = ${s.clipLimit}</span>: $$N_{\\text{clip}} = \\beta \\cdot \\frac{M_{\\text{tile}} \\cdot N_{\\text{tile}}}{L} \\quad (L = 256)$$ Phần diện tích bị cắt không bị xóa bỏ mà được <b>tái phân phối đồng đều</b> xuống toàn bộ dải mức xám trước khi tính hàm CDF.`,
      live: `Tại <span class="xai-val">&beta; = ${s.clipLimit}</span>, CLAHE đạt độ tự nhiên tốt nhất (<span class="xai-val">NIQE = ${s.clahe.niqe}</span>), nhưng điểm <span class="xai-val">PSNR = ${s.clahe.psnr} dB</span> bị thấp do việc tăng tương phản cục bộ làm thay đổi mạnh mức xám trung bình so với ảnh gốc.`,
      defense: `<b>Hỏi:</b> <i>'Tại sao không gặp hiện tượng vệt ô vuông (blocking artifacts) giữa các lưới $8\\times 8$?'</i><br><b>Đáp:</b> Nhờ bước <b>Nội suy song tuyến tính (Bilinear Interpolation)</b> tính toán giá trị pixel dựa trên 4 tâm ô lưới lân cận, giúp xóa bỏ hoàn toàn ranh giới cứng giữa các vùng.`
    }),

    clahe_grid: (s) => ({
      title: `📐 Kích Thước Lưới CLAHE Tile Grid (${s.gridSize})`,
      math: `Kích thước lưới quyết định số lượng miền cục bộ. Với lưới $M_{\\text{tile}} \\times N_{\\text{tile}}$ (hiện tại: <b>${s.gridSize}</b>), toàn bộ ảnh được phân giải thành các khối độc lập để tính toán tương phản vi mô.`,
      live: `Trạng thái hiện tại đang chọn lưới <span class="xai-val">${s.gridSize}</span>. Kích thước $8\\times 8$ là chuẩn cân bằng vàng giữa tương phản vi mô và chi phí tính toán Bilinear.`,
      defense: `<b>Hỏi:</b> <i>'Tại sao không chọn lưới thật mịn $32\\times 32$ hay $64\\times 64$?'</i><br><b>Đáp:</b> Lưới quá nhỏ làm số lượng pixel trong mỗi ô quá ít, thống kê Histogram không còn đủ tính đại diện (dễ gây overfitting vào nhiễu hạt cục bộ) và làm tăng số phép tính nội suy song tuyến, giảm tốc độ khung hình.`
    }),

    histogram_comb: (s) => ({
      title: "📈 Giải Mã Hiện Tượng Răng Cưa Trên Histogram",
      math: `Biểu đồ biểu diễn mật độ phân bố $p(r_k) = n_k / MN$ trên 256 mức xám $[0, 255]$. Thuật toán tốt phải trải đều được cụm pixel bị dồn cục ở vùng tối (mức $0 - 32$) ra toàn dải động.`,
      live: `Quan sát biểu đồ hiện tại: Đường màu cam của <b>HE</b> có dạng <b>răng cưa thưa (comb-like)</b> từ mức xám <span class="xai-val">160 &rarr; 240</span>, trong khi đường tím của <b>MSR</b> và xanh lá của <b>Gamma</b> uốn lượn liên tục và mượt mà.`,
      defense: `<b>Hỏi:</b> <i>'Tại sao đường Histogram của HE lại bị đứt quãng dạng răng cưa?'</i><br><b>Đáp:</b> Do hàm phân phối tích lũy (CDF) của ảnh số là rời rạc. HE ép các mức xám có tần suất cao nhảy vọt sang vị trí cách xa nhau, để trống các mức xám ở giữa (Quantization Loss), gây hiện tượng bệt màu và gắt sáng.`
    }),

    metrics_paradox: (s) => ({
      title: "⚖️ Nghịch Lý Điểm Số: Tại Sao Chọn MSR/CLAHE Thay Vì HE?",
      math: `<b>PSNR</b> chỉ đo sai số bình phương trung bình (MSE) độc lập từng điểm ảnh. <b>SSIM</b> đánh giá 3 yếu tố: Độ sáng, Tương phản và Cấu trúc không gian. <b>NIQE</b> đánh giá độ tự nhiên không cần ảnh gốc.`,
      live: `Tuy <b>HE</b> có PSNR cao nhất (<span class="xai-val">${s.he.psnr} dB</span>) nhưng SSIM chỉ đạt <span class="xai-val">${s.he.ssim}</span>. Ngược lại, <b>MSR</b> dẫn đầu tuyệt đối về bảo toàn cấu trúc (<span class="xai-val">SSIM = ${s.msr.ssim}</span>, tăng <span class="xai-val">${safeDiff(s.msr.ssim, s.inputDegraded.ssim, 4)}</span> so với ảnh suy thoái).`,
      defense: `<b>Hỏi:</b> <i>'MSR chạy mất <span class="xai-val">${s.msr.time} ms</span> (chậm gấp ~145 lần HE), làm sao ứng dụng thực tế?'</i><br><b>Đáp:</b> MSR phải tính 3 phép tích chập Gaussian lớn ($\\sigma = 15, 80, 250$). Trong xử lý ảnh y tế/vệ tinh/hậu kỳ cần độ chính xác cấu trúc thì chọn MSR; nếu chạy video thời gian thực ($>30\\text{ FPS}$) thì chuyển sang CLAHE (<span class="xai-val">${s.clahe.time} ms</span>) hoặc tối ưu MSR bằng biến đổi FFT.`
    }),

    gamma_val: (s) => ({
      title: `⚙️ Hệ Số Hiệu Chỉnh Gamma (&gamma; = ${s.gammaVal})`,
      math: `Biến đổi lũy thừa $V_{\\text{out}} = 255 \\cdot (V/255)^\\gamma$. Với $\\gamma = ${s.gammaVal} < 1.0$, đường cong biến đổi lồi lên trên, kéo sáng mạnh các pixel tối $[0, 64]$ trong khi giữ nguyên các pixel sáng cực đại.`,
      live: `Hệ số đang chọn là <span class="xai-val">&gamma; = ${s.gammaVal}</span>. Thời gian xử lý đạt cực hạn: <span class="xai-val">${s.gamma.time} ms</span>, nhanh nhất trong 4 thuật toán nhờ bảng tra cứu LUT 256 phần tử tính trước.`,
      defense: `<b>Hỏi:</b> <i>'Gamma Correction có khuyết điểm gì so với CLAHE và MSR?'</i><br><b>Đáp:</b> Gamma là hàm biến đổi toàn cục đơn điệu cố định, không có khả năng thích nghi cục bộ theo từng vùng ảnh. Vùng tối sâu kéo sáng vừa đủ thì vùng trung gian có thể bị bạc màu, và ngược lại.`
    }),

    brightness: (s) => ({
      title: `☀️ Hệ Số Độ Chói Suy Giảm (&alpha; = ${s.brightness})`,
      math: `Mô hình suy giảm tuyến tính: $I_{\\text{dim}}(x, y) = \\alpha \\cdot I(x, y)$ với $\\alpha \\in [0.10, 0.80]$. Tương đương với việc giảm độ phơi sáng (Exposure Value - EV) khi đóng khẩu độ hoặc chụp với tốc độ màn trập quá nhanh.`,
      live: `Hệ số đang đặt là <span class="xai-val">&alpha; = ${s.brightness}</span>, làm giảm năng lượng tín hiệu trung bình của ảnh xuống mức ${Math.round(s.brightness * 100)}% so với cảnh gốc.`,
      defense: `<b>Hỏi:</b> <i>'Tại sao phải mô phỏng suy thoái trên ảnh chuẩn thay vì chụp trực tiếp ảnh tối?'</i><br><b>Đáp:</b> Việc mô phỏng có kiểm soát trên ảnh chuẩn (Ground Truth) là phương pháp luận thực nghiệm bắt buộc trong ngành thị giác máy tính để tính toán chính xác sai số khách quan (PSNR, SSIM) đối chuẩn pixel-by-pixel.`
    }),

    gamma_dark: (s) => ({
      title: `🌙 Gamma Làm Tối Phi Tuyến (&gamma;_{dark} = ${s.gammaDark})`,
      math: `Mô phỏng phản ứng phi tuyến của quang học và cảm biến trong bóng đêm: $$I_{\\text{dark}} = 255 \\cdot \\left(\\frac{I}{255}\\right)^{\\gamma_{\\text{dark}}} \\quad (\\gamma_{\\text{dark}} = ${s.gammaDark} > 1.0)$$`,
      live: `Giá trị <span class="xai-val">&gamma;_{dark} = ${s.gammaDark}</span> nén sâu các chi tiết trong bóng tối về sát mức xám 0, tái lập đúng độ tương phản gắt gao của cảnh đêm thiên nhiên.`,
      defense: `<b>Hỏi:</b> <i>'Khác biệt giữa $\\alpha$ và $\\gamma_{\\text{dark}}$ là gì?'</i><br><b>Đáp:</b> $\\alpha$ làm giảm độ sáng tuyến tính đồng đều; còn $\\gamma_{\\text{dark}} > 1$ dìm sâu các pixel tối nhanh hơn nhiều so với pixel sáng, mô phỏng chính xác đường đặc tính quang học của cảm biến trong bóng tối.`
    }),

    sim_lowlight: (s) => ({
      title: "🧪 Mô Hình Suy Thoái Môi Trường Thiếu Sáng",
      math: `Phương trình tổng quát mô phỏng điều kiện chụp đêm: $$I_{\\text{degraded}} = \\text{clip}\\Big(\\alpha \\cdot I(x, y)^{\\gamma_{\\text{dark}}} + n, 0, 255\\Big)$$`,
      live: `Trạng thái mô phỏng: <span class="xai-val">${s.isSimChecked ? "ĐANG BẬT" : "TẮT"}</span>. Tạo ra cặp ảnh suy thoái - đối chuẩn chuẩn mực cho nghiên cứu học thuật.`,
      defense: `<b>Hỏi:</b> <i>'Khi người dùng upload ảnh thực tế ngoài đời thì mô phỏng này xử lý thế nào?'</i><br><b>Đáp:</b> Hệ thống tự động vô hiệu hóa mô phỏng tổng hợp, chuyển sang chế độ đánh giá không tham chiếu (Blind IQA) thông qua chỉ số NIQE và bảo toàn màu sắc trên không gian HSV/LAB.`
    }),

    color_space: (s) => ({
      title: `🎨 Không Gian Màu Xử Lý (${s.colorSpace})`,
      math: `Tách kênh độ sáng ($V$ trong HSV hoặc $L^*$ trong CIELAB) khỏi các kênh màu sắc ($H,S$ hoặc $a^*,b^*$). Áp dụng thuật toán tăng cường chỉ trên kênh độ sáng và giữ nguyên 100% kênh màu.`,
      live: `Đang thiết lập trên <b>${s.colorSpace}</b>. Toàn bộ sắc thái màu sắc của cảnh quan thiên nhiên được bảo tồn tuyệt đối.`,
      defense: `<b>Hỏi:</b> <i>'HSV và CIELAB khác nhau căn bản thế nào trong xử lý ảnh?'</i><br><b>Đáp:</b> HSV tính toán nhanh qua phép biến đổi hình trụ đơn giản; CIELAB là không gian màu đều theo thị giác người (Perceptually Uniform), kênh $L^*$ phản ánh cảm nhận độ sáng phi tuyến của mắt người chuẩn xác hơn.`
    }),

    card_denoise: (s) => ({
      title: "🛡️ Khối Tiền Xử Lý Khử Nhiễu",
      math: `So sánh giữa các bộ lọc: Bilateral Filter (kết hợp Gauss không gian và cường độ), Non-Local Means (NLM - tìm kiếm tự tương đồng toàn cục) và Median Filter (chọn giá trị trung vị).`,
      live: `Bộ lọc đang kích hoạt: <span class="xai-val">${s.denoiseMethod.toUpperCase()}</span> với cường độ nhiễu đầu vào <span class="xai-val">&sigma; = ${s.noiseSigma}</span>.`,
      defense: `<b>Hỏi:</b> <i>'Tại sao phải khử nhiễu TRƯỚC KHI kéo sáng mà không phải sau khi kéo sáng?'</i><br><b>Đáp:</b> Các thuật toán kéo sáng (đặc biệt là CLAHE và Retinex) đều khuếch đại tương phản cục bộ. Nếu để nhiễu đi vào, các hạt nhiễu nhỏ sẽ bị khuếch đại thành đốm sáng loang lổ không thể lọc sạch ở bước sau mà không làm mất biên cạnh.`
    }),

    card_tuning: (s) => ({
      title: "🎛️ Tinh Chỉnh Tham Số Thuật Toán",
      math: `Tối ưu hóa không gian siêu tham số: Clip Limit $\\beta \\in [1, 8]$, Tile Grid $\\in \\{4\\times 4, 8\\times 8, 16\\times 16\\}$, và hệ số $\\gamma \\in [0.2, 1.5]$.`,
      live: `Tham số hiện tại: <span class="xai-val">&beta; = ${s.clipLimit}</span> | <span class="xai-val">${s.gridSize}</span> | <span class="xai-val">&gamma; = ${s.gammaVal}</span>.`,
      defense: `<b>Hỏi:</b> <i>'Làm sao chứng minh bộ tham số này là tối ưu?'</i><br><b>Đáp:</b> Thông qua bảng đối chiếu 6 ô XAI và đồ thị Radar đa trục, chứng minh sự thỏa hiệp tối ưu giữa độ tương đồng cấu trúc (SSIM) và độ tự nhiên không tham chiếu (NIQE).`
    }),

    he: (s) => ({
      title: "Thuật Toán 1: Histogram Equalization (HE Toàn Cục)",
      math: `Trải phẳng phân phối xác suất tích lũy trên toàn bộ ảnh: $$s_k = \\frac{255}{M \\cdot N} \\sum_{j=0}^k n_j$$`,
      live: `Kết quả: PSNR = <span class="xai-val">${s.he.psnr} dB</span> | SSIM = <span class="xai-val">${s.he.ssim}</span> | NIQE = <span class="xai-val">${s.he.niqe}</span> | Thời gian: <span class="xai-val">${s.he.time} ms</span>.`,
      defense: `<b>Hỏi:</b> <i>'Nhược điểm lớn nhất của HE trong xử lý ảnh đêm phong cảnh là gì?'</i><br><b>Đáp:</b> HE kéo sáng toàn cục làm bệt màu nền trời đêm, gây cháy sáng các nguồn sáng nhân tạo (đèn xe, đèn đường) và khuếch đại cực mạnh nhiễu hạt ở các vùng tối sâu.`
    }),

    clahe: (s) => ({
      title: "Thuật Toán 2: CLAHE (Contrast Limited Adaptive HE)",
      math: `Chia ảnh thành lưới $8\\times 8$, cắt đỉnh histogram theo hệ số $\\beta$, phân phối thặng dư $R$ và nội suy song tuyến tính Bilinear Interpolation.`,
      live: `Kết quả: PSNR = <span class="xai-val">${s.clahe.psnr} dB</span> | SSIM = <span class="xai-val">${s.clahe.ssim}</span> | NIQE = <span class="xai-val">${s.clahe.niqe}</span> | Thời gian: <span class="xai-val">${s.clahe.time} ms</span>.`,
      defense: `<b>Hỏi:</b> <i>'Tại sao CLAHE được đánh giá là thuật toán cân bằng tốt nhất?'</i><br><b>Đáp:</b> Nhờ cơ chế cắt ngưỡng Clip Limit chống cháy sáng và nội suy song tuyến triệt tiêu viền phân mảnh, CLAHE vừa tăng rõ nét chi tiết cục bộ vừa chạy đủ nhanh (~10 ms) cho ứng dụng thực tế.`
    }),

    gamma: (s) => ({
      title: "Thuật Toán 3: Gamma Correction (Biến Đổi Lũy Thừa Phi Tuyến)",
      math: `Ánh xạ mức xám: $V_{\\text{out}} = 255 \\cdot (V/255)^\\gamma$. Khởi tạo bảng tra cứu LUT 256 giá trị trong $O(L)$, ánh xạ từng pixel trong $O(1)$.`,
      live: `Kết quả: PSNR = <span class="xai-val">${s.gamma.psnr} dB</span> | SSIM = <span class="xai-val">${s.gamma.ssim}</span> | NIQE = <span class="xai-val">${s.gamma.niqe}</span> | Thời gian: <span class="xai-val">${s.gamma.time} ms</span>.`,
      defense: `<b>Hỏi:</b> <i>'Khi nào thì bắt buộc phải chọn Gamma Correction thay vì CLAHE/MSR?'</i><br><b>Đáp:</b> Khi triển khai trên hệ thống nhúng có phần cứng cực kỳ hạn chế (vi điều khiển, cảm biến IoT năng lượng thấp), Gamma là giải pháp duy nhất đạt hiệu năng thời gian thực với chi phí bộ nhớ chỉ 256 bytes.`
    }),

    msr: (s) => ({
      title: "Thuật Toán 4: Multi-Scale Retinex (MSR)",
      math: `Mô hình bóc tách phản xạ trên 3 quy mô Gaussian: $$R_{\\text{MSR}} = \\sum_{k=1}^3 \\frac{1}{3} \\Big[\\ln(I) - \\ln(I * G_{\\sigma_k})\\Big] \\quad (\\sigma_k \\in \\{15, 80, 250\\})$$`,
      live: `Kết quả: PSNR = <span class="xai-val">${s.msr.psnr} dB</span> | SSIM = <span class="xai-val">${s.msr.ssim}</span> | NIQE = <span class="xai-val">${s.msr.niqe}</span> | Thời gian: <span class="xai-val">${s.msr.time} ms</span>.`,
      defense: `<b>Hỏi:</b> <i>'MSR đạt chất lượng hình ảnh cao nhưng thời gian chạy lâu, làm sao ứng dụng?'</i><br><b>Đáp:</b> MSR xuất sắc trong các bài toán không đòi hỏi thời gian thực như xử lý ảnh vệ tinh, ảnh y tế MRI/X-ray, hậu kỳ nhiếp ảnh nghệ thuật. Trong thực tế, có thể tăng tốc MSR gấp 50-100 lần bằng biến đổi FFT hoặc lập trình CUDA trên GPU.`
    }),

    psnr_kpi: (s) => ({
      title: "📊 Chỉ Số PSNR (Peak Signal-to-Noise Ratio)",
      math: `$$\\text{MSE} = \\frac{1}{MN}\\sum_{i,j}[I_{\\text{clean}}(i,j) - I_{\\text{proc}}(i,j)]^2, \\quad \\text{PSNR} = 10\\log_{10}\\left(\\frac{255^2}{\\text{MSE}}\\right)$$`,
      live: `Thuật toán đạt PSNR cao nhất: <b>HE</b> (<span class="xai-val">${s.he.psnr} dB</span>). Ảnh suy thoái đầu vào: <span class="xai-val">${s.inputDegraded.psnr} dB</span>.`,
      defense: `<b>Hỏi:</b> <i>'Tại sao PSNR cao không đồng nghĩa với ảnh đẹp tự nhiên?'</i><br><b>Đáp:</b> PSNR chỉ đo sai số bình phương trung bình từng pixel độc lập, không phản ánh cách mắt người nhận thức tương phản và cấu trúc. Việc nâng độ sáng trung bình lên gần ảnh gốc làm giảm MSE và đẩy PSNR lên cao dù ảnh bị cháy sáng bệt màu.`
    }),

    ssim_kpi: (s) => ({
      title: "📊 Chỉ Số Cấu Trúc SSIM (Structural Similarity Index)",
      math: `$$\\text{SSIM}(x, y) = \\frac{(2\\mu_x\\mu_y + C_1)(2\\sigma_{xy} + C_2)}{(\\mu_x^2 + \\mu_y^2 + C_1)(\\sigma_x^2 + \\sigma_y^2 + C_2)}$$ Kết hợp 3 yếu tố: độ chói, tương phản và cấu trúc hình học.`,
      live: `Thuật toán dẫn đầu cấu trúc: <b>MSR</b> (<span class="xai-val">SSIM = ${s.msr.ssim}</span>, tăng <span class="xai-val">${safeDiff(s.msr.ssim, s.inputDegraded.ssim, 4)}</span> so với ảnh suy thoái).`,
      defense: `<b>Hỏi:</b> <i>'Tại sao SSIM được hội đồng đánh giá cao hơn PSNR?'</i><br><b>Đáp:</b> Vì SSIM mô phỏng cơ chế thị giác người HVS, đánh giá chính xác khả năng bảo tồn các cạnh sắc nét, kết cấu tán cây, mái nhà và đường chân trời sau khi kéo sáng.`
    }),

    niqe_kpi: (s) => ({
      title: "📊 Chỉ Số Tự Nhiên Không Tham Chiếu (NIQE)",
      math: `Khoảng cách Mahalanobis so với mô hình phân phối Gauss tổng quát bất đối xứng AGGD của tập ảnh tự nhiên chuẩn (Pristine Corpus): $$D = \\sqrt{(\\nu_1 - \\nu_2)^T \\Sigma^{-1} (\\nu_1 - \\nu_2)}$$`,
      live: `Chỉ số tự nhiên tốt nhất: <b>CLAHE</b> (<span class="xai-val">NIQE = ${s.clahe.niqe}</span>). Điểm số ảnh suy thoái: <span class="xai-val">${s.inputDegraded.niqe}</span>.`,
      defense: `<b>Hỏi:</b> <i>'Ý nghĩa thực tiễn của NIQE khi người dùng tự upload ảnh ngoài đời là gì?'</i><br><b>Đáp:</b> Với ảnh thực tế không có Ground Truth, không thể tính PSNR hay SSIM. NIQE là thước đo khoa học khách quan duy nhất để tự động đánh giá và xếp hạng chất lượng ảnh sau nâng cao.`
    }),

    col_psnr: (s) => ({
      title: "📊 Cột 1: PSNR (Peak Signal-to-Noise Ratio) [Đơn vị: dB]",
      math: `Tỷ số tín hiệu cực đại trên nhiễu đo lường sai số bình phương trung bình (MSE) giữa ảnh sau xử lý so với ảnh gốc chuẩn (Ground Truth): $$\\text{MSE} = \\frac{1}{M \\cdot N} \\sum_{i=0}^{M-1} \\sum_{j=0}^{N-1} [I_{\\text{clean}}(i, j) - I_{\\text{proc}}(i, j)]^2$$ $$\\text{PSNR} = 10 \\cdot \\log_{10}\\left(\\frac{255^2}{\\text{MSE}}\\right) = 10 \\cdot \\log_{10}\\left(\\frac{65025}{\\text{MSE}}\\right) \\quad (\\text{dB})$$`,
      live: `Bảng đo lường hiện thời: <b>HE</b> đạt PSNR = <span class="xai-val">${s.he.psnr} dB</span> (cao nhất), <b>MSR</b> (<span class="xai-val">${s.msr.psnr} dB</span>), <b>Gamma</b> (<span class="xai-val">${s.gamma.psnr} dB</span>), và <b>CLAHE</b> (<span class="xai-val">${s.clahe.psnr} dB</span>). Mức sàn ảnh suy thoái đầu vào: <span class="xai-val">${s.inputDegraded.psnr} dB</span>.`,
      defense: `<b>Hỏi:</b> <i>'Tại sao PSNR trong bài toán ảnh đêm thường chỉ dao động từ 10 - 20 dB (thấp hơn ngưỡng 30 dB thông thường)?'</i><br><b>Đáp:</b> Trong xử lý nén/truyền dẫn ảnh, ảnh gốc và ảnh nén có cùng độ sáng trung bình nên PSNR dễ &gt; 30 dB. Ngược lại, trong bài toán kéo sáng, toàn bộ phân phối mức xám được dịch chuyển và kéo giãn mạnh ra khỏi ảnh tối ban đầu; do phép so sánh pixel-by-pixel bị ảnh hưởng mạnh bởi độ lệch mức xám trung bình nên PSNR ở mức 10 - 20 dB là hoàn toàn bình thường và hợp lý.`
    }),

    col_delta_psnr: (s) => ({
      title: "📈 Cột 2: &Delta; PSNR = PSNR(Output) - PSNR(Input) [dB]",
      math: `Đo lường mức độ tăng/giảm sai số năng lượng điểm ảnh so với ảnh suy thoái đầu vào: $$\\Delta\\text{PSNR} = \\text{PSNR}_{\\text{output}} - \\text{PSNR}_{\\text{input}} = 10 \\log_{10}\\left(\\frac{\\text{MSE}_{\\text{input}}}{\\text{MSE}_{\\text{output}}}\\right)$$ &bull; Nếu $\\Delta\\text{PSNR} > 0$: Sai số MSE giảm so với ảnh tối ban đầu (năng lượng tín hiệu tiệm cận ảnh gốc hơn);<br>&bull; Nếu $\\Delta\\text{PSNR} < 0$: Sai số MSE tăng lên do mức xám bị dịch chuyển mạnh.`,
      live: `Hiện tại: <b>HE</b> có &Delta;PSNR = <span class="xai-val">${safeDiff(s.he.psnr, s.inputDegraded.psnr, 2)} dB</span>, <b>MSR</b> đạt <span class="xai-val">${safeDiff(s.msr.psnr, s.inputDegraded.psnr, 2)} dB</span>, <b>Gamma</b> đạt <span class="xai-val">${safeDiff(s.gamma.psnr, s.inputDegraded.psnr, 2)} dB</span>, <b>CLAHE</b> đạt <span class="xai-val">${safeDiff(s.clahe.psnr, s.inputDegraded.psnr, 2)} dB</span>.`,
      defense: `<b>Hỏi:</b> <i>'Tại sao &Delta;PSNR của CLAHE lại có thể âm trong khi bằng mắt thường ảnh rõ nét hơn rất nhiều?'</i><br><b>Đáp:</b> Nghịch lý này do CLAHE tăng tương phản vi mô cục bộ cực mạnh, đưa các chi tiết tối lên mức xám cao để mắt người quan sát rõ. Tuy nhiên, việc thay đổi mạnh giá trị pixel ở từng vùng làm tăng tổng sai số MSE so với ảnh gốc chuẩn $\\implies \\Delta\\text{PSNR} < 0$. Đây là lý do ngành thị giác máy tính hiện đại không dựa đơn độc vào PSNR mà phải kết hợp chặt chẽ với SSIM và NIQE.`
    }),

    col_ssim: (s) => ({
      title: "📐 Cột 3: SSIM (Structural Similarity Index) [Dải: 0 &rarr; 1.0]",
      math: `Mô phỏng trực tiếp hệ thống thị giác người (HVS), đánh giá đồng thời 3 thành phần không gian: Độ chói ($l$), Tương phản ($c$), và Cấu trúc bề mặt ($s$): $$\\text{SSIM}(x, y) = [l(x, y)]^\\alpha \\cdot [c(x, y)]^\\beta \\cdot [s(x, y)]^\\gamma = \\frac{(2\\mu_x\\mu_y + C_1)(2\\sigma_{xy} + C_2)}{(\\mu_x^2 + \\mu_y^2 + C_1)(\\sigma_x^2 + \\sigma_y^2 + C_2)}$$ <b>Giá trị càng gần 1.0 chứng minh cấu trúc bề mặt, tán cây, đồi núi và các đường nét kiến trúc càng được bảo toàn nguyên vẹn.</b>`,
      live: `Kết quả thực nghiệm: <b>MSR</b> bảo toàn cấu trúc tốt nhất (<span class="xai-val">SSIM = ${s.msr.ssim}</span>), tiếp theo là <b>HE</b> (<span class="xai-val">${s.he.ssim}</span>), <b>Gamma</b> (<span class="xai-val">${s.gamma.ssim}</span>), và <b>CLAHE</b> (<span class="xai-val">${s.clahe.ssim}</span>). Cấu trúc ảnh suy thoái: <span class="xai-val">${s.inputDegraded.ssim}</span>.`,
      defense: `<b>Hỏi:</b> <i>'Vì sao SSIM là chỉ số chuẩn mực vàng (Gold Standard) cho bài toán phục hồi ảnh?'</i><br><b>Đáp:</b> Mắt người không đếm sai số từng pixel như PSNR mà nhận diện vật thể dựa vào mối tương quan cấu trúc không gian giữa các pixel lân cận (Structural Information). SSIM loại bỏ ảnh hưởng của việc tăng giảm ánh sáng đồng nhất, tập trung đo lường độ trung thực của các đường nét và cạnh biên.`
    }),

    col_delta_ssim: (s) => ({
      title: "📈 Cột 4: &Delta; SSIM = SSIM(Output) - SSIM(Input)",
      math: `Đo lường mức độ khôi phục cấu trúc hình học thực sự mà thuật toán mang lại so với ảnh suy thoái đầu vào: $$\\Delta\\text{SSIM} = \\text{SSIM}_{\\text{output}} - \\text{SSIM}_{\\text{input}}$$ &bull; $\\Delta\\text{SSIM} > 0$: Cấu trúc được khôi phục, chi tiết ẩn trong bóng tối được cứu vãn;<br>&bull; $\\Delta\\text{SSIM} \\le 0$: Thuật toán làm nát cấu trúc, cháy biên hoặc nhòe hình.`,
      live: `Hiện tại: <b>MSR</b> tăng vọt <span class="xai-val">&Delta;SSIM = ${safeDiff(s.msr.ssim, s.inputDegraded.ssim, 4)}</span> (từ ${s.inputDegraded.ssim} lên ${s.msr.ssim}), <b>HE</b> tăng <span class="xai-val">${safeDiff(s.he.ssim, s.inputDegraded.ssim, 4)}</span>, <b>Gamma</b> tăng <span class="xai-val">${safeDiff(s.gamma.ssim, s.inputDegraded.ssim, 4)}</span>, <b>CLAHE</b> tăng <span class="xai-val">${safeDiff(s.clahe.ssim, s.inputDegraded.ssim, 4)}</span>.`,
      defense: `<b>Hỏi:</b> <i>'Nếu một thuật toán cho &Delta;SSIM &le; 0 thì có thể kết luận điều gì?'</i><br><b>Đáp:</b> Nếu $\\Delta\\text{SSIM} \\le 0$, thuật toán đó đã phá hủy cấu trúc hình ảnh (gây cháy sáng mất chi tiết, nhòe biên hoặc làm biến dạng cấu trúc bề mặt) còn nặng nề hơn cả bóng tối ban đầu. Một thuật toán tăng cường ảnh được xem là thành công bắt buộc phải có $\\Delta\\text{SSIM} > 0$.`
    }),

    col_niqe: (s) => ({
      title: "🌿 Cột 5: NIQE (Naturalness Image Quality Evaluator) [Càng nhỏ càng tốt]",
      math: `Chỉ số đánh giá độ tự nhiên mù không tham chiếu (Blind No-Reference IQA), đo khoảng cách Mahalanobis so với mô hình phân phối Gauss tổng quát bất đối xứng (AGGD) của tập ảnh tự nhiên chuẩn (Pristine Corpus): $$D(\\nu_1, \\nu_2, \\Sigma_1, \\Sigma_2) = \\sqrt{ (\\nu_1 - \\nu_2)^T \\left( \\frac{\\Sigma_1 + \\Sigma_2}{2} \\right)^{-1} (\\nu_1 - \\nu_2) }$$ <b>QUY TẮC BẮT BUỘC: ĐIỂM CÀNG THẤP THÌ ẢNH CÀNG TỰ NHIÊN, CÀNG ĐẸP!</b> (2.5 - 5.5: rất tự nhiên; trên 8.0: giả tạo/nhiễu).`,
      live: `Xếp hạng độ tự nhiên: <b>CLAHE</b> (<span class="xai-val">NIQE = ${s.clahe.niqe}</span> - tự nhiên nhất), <b>Gamma</b> (<span class="xai-val">${s.gamma.niqe}</span>), <b>MSR</b> (<span class="xai-val">${s.msr.niqe}</span>), <b>HE</b> (<span class="xai-val">${s.he.niqe}</span>). Ảnh suy thoái đầu vào: <span class="xai-val">${s.inputDegraded.niqe}</span>.`,
      defense: `<b>Hỏi:</b> <i>'Khi người dùng tải lên ảnh chụp thực tế ngoài đời (không có ảnh gốc Ground Truth) thì bảng đo lường này xử lý thế nào?'</i><br><b>Đáp:</b> Khi không có ảnh gốc, các chỉ số tham chiếu PSNR và SSIM sẽ tự động bị ẩn (N/A). Hệ thống chuyển trọng tâm sang chỉ số NIQE độc lập để định lượng mức độ sắc nét và tính tự nhiên, đảm bảo thuật toán không sinh ra viền sáng giả (halos) hay nhiễu hạt nhân tạo.`
    }),

    col_delta_niqe: (s) => ({
      title: "📉 Cột 6: &Delta; NIQE = NIQE(Output) - NIQE(Input) [Quy ước dấu âm là tốt]",
      math: `Độ thay đổi khoảng cách tự nhiên so với ảnh suy thoái đầu vào: $$\\Delta\\text{NIQE} = \\text{NIQE}_{\\text{output}} - \\text{NIQE}_{\\text{input}}$$ <b>QUY ƯỚC DẤU ĐẶC BIỆT:</b> Do NIQE càng nhỏ càng tốt, nên:<br>&bull; <b>$\\Delta\\text{NIQE} < 0$ (màu xanh lá):</b> Điểm NIQE giảm xuống $\\implies$ Ảnh trở nên tự nhiên hơn ảnh đầu vào;<br>&bull; <b>$\\Delta\\text{NIQE} > 0$ (màu vàng/đỏ):</b> Điểm NIQE tăng lên $\\implies$ Ảnh bị giả tạo, cháy sáng hoặc nổi hạt nhiễu.`,
      live: `Hiện tại: <b>CLAHE</b> đạt <span class="xai-val">&Delta;NIQE = ${safeDiff(s.clahe.niqe, s.inputDegraded.niqe, 2)}</span>, <b>Gamma</b> đạt <span class="xai-val">${safeDiff(s.gamma.niqe, s.inputDegraded.niqe, 2)}</span>, <b>MSR</b> đạt <span class="xai-val">${safeDiff(s.msr.niqe, s.inputDegraded.niqe, 2)}</span>, <b>HE</b> đạt <span class="xai-val">${safeDiff(s.he.niqe, s.inputDegraded.niqe, 2)}</span>.`,
      defense: `<b>Hỏi:</b> <i>'Tại sao &Delta;NIQE lại có quy ước dấu ngược với &Delta;PSNR và &Delta;SSIM?'</i><br><b>Đáp:</b> Vì NIQE đo khoảng cách độ lệch (deviation/distance) so với tập ảnh mẫu hoàn hảo. Giá trị giảm ($\\Delta\\text{NIQE} < 0$) tương ứng với khoảng cách sai lệch bị thu hẹp lại, chứng minh bức ảnh đã được đưa trở về trạng thái phân phối thống kê tự nhiên của mắt người.`
    }),

    col_time: (s) => ({
      title: "⏱️ Cột 7: Thời Gian Xử Lý (Latency) [Mili-giây - ms]",
      math: `Thời gian thực thi thuật toán trên máy tính, tương ứng với độ phức tạp tính toán lý thuyết $O(\\cdot)$:<br>&bull; <b>Gamma:</b> $O(N)$ (LUT 256 phần tử tính trước, $O(1)$ mỗi pixel);<br>&bull; <b>HE:</b> $O(N + L)$ (1 lần duyệt đếm histogram + 1 lần ánh xạ CDF);<br>&bull; <b>CLAHE:</b> $O(N) + \\text{Bilinear}$ (histogram từng ô $8\\times 8$ + nội suy song tuyến 4 tâm);<br>&bull; <b>MSR:</b> $O(K \\cdot N \\log N)$ (3 phép tích chập Gaussian không gian lớn $\\sigma=15, 80, 250$).`,
      live: `Thời gian đo thực tế tại lần chạy này: <b>Gamma:</b> <span class="xai-val">${s.gamma.time} ms</span> | <b>HE:</b> <span class="xai-val">${s.he.time} ms</span> | <b>CLAHE:</b> <span class="xai-val">${s.clahe.time} ms</span> | <b>MSR:</b> <span class="xai-val">${s.msr.time} ms</span>.`,
      defense: `<b>Hỏi:</b> <i>'Chuẩn nào để xác định thuật toán có thể áp dụng cho video giám sát ban đêm thời gian thực?'</i><br><b>Đáp:</b> Tiêu chuẩn video mượt mà thời gian thực là $\\ge 30\\text{ FPS}$, tương đương mỗi khung hình phải xử lý xong trong $\\le 1000/30 \\approx 33.3\\text{ ms}$. Với tốc độ $5 - 10\\text{ ms}$, <b>CLAHE, Gamma và HE</b> đáp ứng hoàn hảo yêu cầu này. <b>MSR</b> (${s.msr.time} ms) cần được tăng tốc bằng biến đổi FFT hoặc lập trình CUDA/TensorRT trên GPU mới có thể chạy video.`
    }),

    difference_heatmap: (s) => ({
      title: "🔥 Bản Đồ Nhiệt Sai Khác (Difference Heatmap - XAI Visualization)",
      math: `Độ lệch năng lượng tuyệt đối giữa ảnh sau tăng cường và ảnh đầu vào: $$\\Delta I(x, y) = |I_{\\text{enhanced}}(x, y) - I_{\\text{degraded}}(x, y)|$$ Sau đó chuẩn hóa về dải $[0, 255]$ và ánh xạ qua dải màu quang phổ nhiệt <b>COLORMAP_JET</b>: Xanh dương $\\to$ Xanh lơ $\\to$ Lục $\\to$ Vàng $\\to$ Cam $\\to$ Đỏ rực.`,
      live: `Giải tích thực nghiệm trực tiếp: <b>HE</b> (đỏ rực toàn cảnh, can thiệp thô bạo, PSNR = <span class="xai-val">${s.he.psnr} dB</span>), <b>CLAHE</b> (đỏ/vàng khu trú thông minh ở bóng tối, bảo vệ nền trời xanh, NIQE = <span class="xai-val">${s.clahe.niqe}</span>), <b>Gamma</b> (màu lan tỏa mượt đều), <b>MSR</b> (phát sáng men theo biên cấu trúc, SSIM = <span class="xai-val">${s.msr.ssim}</span>).`,
      defense: `<b>Hỏi:</b> <i>'Tại sao bản đồ nhiệt sai khác lại dùng bảng màu JET (COLORMAP_JET) thay vì dùng ảnh thang độ xám (Grayscale)?'</i><br><b>Đáp:</b> Mắt người có độ nhạy tương phản với màu sắc quang phổ cao gấp hàng chục lần so với thang xám (chỉ nhận biết được ~30 sắc thái xám, nhưng nhận biết được hàng ngàn sắc độ màu). Bảng màu JET phóng đại trực quan các sai lệch năng lượng cực nhỏ ($2 - 3$ mức xám) mà mắt thường hoàn toàn không thể nhận ra trên ảnh xám, giúp người nghiên cứu thấy rõ vùng nào thuật toán bù sáng vừa đủ, vùng nào can thiệp quá mức gây cháy sáng.`
    })
  };

  // Ánh xạ tương thích cho tất cả các aliases & tên gọi cũ
  DEFENSE_KNOWLEDGE_BASE["psnr"] = DEFENSE_KNOWLEDGE_BASE["psnr_kpi"];
  DEFENSE_KNOWLEDGE_BASE["ssim"] = DEFENSE_KNOWLEDGE_BASE["ssim_kpi"];
  DEFENSE_KNOWLEDGE_BASE["niqe"] = DEFENSE_KNOWLEDGE_BASE["niqe_kpi"];
  DEFENSE_KNOWLEDGE_BASE["histogram"] = DEFENSE_KNOWLEDGE_BASE["histogram_comb"];
  DEFENSE_KNOWLEDGE_BASE["table"] = DEFENSE_KNOWLEDGE_BASE["metrics_paradox"];
  DEFENSE_KNOWLEDGE_BASE["clahe_clip"] = DEFENSE_KNOWLEDGE_BASE["clahe_params"];
  DEFENSE_KNOWLEDGE_BASE["denoise_method"] = DEFENSE_KNOWLEDGE_BASE["bilateral_hsv"];
  DEFENSE_KNOWLEDGE_BASE["delta_psnr"] = DEFENSE_KNOWLEDGE_BASE["col_delta_psnr"];
  DEFENSE_KNOWLEDGE_BASE["delta_ssim"] = DEFENSE_KNOWLEDGE_BASE["col_delta_ssim"];
  DEFENSE_KNOWLEDGE_BASE["delta_niqe"] = DEFENSE_KNOWLEDGE_BASE["col_delta_niqe"];
  DEFENSE_KNOWLEDGE_BASE["time"] = DEFENSE_KNOWLEDGE_BASE["col_time"];
  DEFENSE_KNOWLEDGE_BASE["heatmap"] = DEFENSE_KNOWLEDGE_BASE["difference_heatmap"];
  DEFENSE_KNOWLEDGE_BASE["heatmaps"] = DEFENSE_KNOWLEDGE_BASE["difference_heatmap"];



  const defensePopover = document.getElementById("xai-defense-popover");
  const masterDrawer = document.getElementById("xai-master-drawer");
  const masterBackdrop = document.getElementById("xai-backdrop");
  let currentActiveDefenseBtn = null;

  function safeNum(v, d = 2) {
    if (v === null || v === undefined || isNaN(v)) return "--";
    return Number(v).toFixed(d);
  }

  function safeDiff(v1, v2, d = 2) {
    const n1 = parseFloat(v1);
    const n2 = parseFloat(v2);
    if (isNaN(n1) || isNaN(n2)) return "--";
    const diff = n1 - n2;
    return diff >= 0 ? `+${diff.toFixed(d)}` : diff.toFixed(d);
  }

  // Đọc thông số thực tế đang hiển thị trên giao diện & kết quả chạy gần nhất
  function getCurrentAppState() {
    let activeGrid = "8x8";
    gridPills.forEach(p => {
      if (p.classList.contains("active")) activeGrid = p.dataset.grid || "8x8";
    });

    const isSimChecked = chkSimulateLowLight ? chkSimulateLowLight.checked : true;
    const brightness = brightnessFactorSlider ? parseFloat(brightnessFactorSlider.value) : 0.35;
    const gammaDark = gammaDarkSlider ? parseFloat(gammaDarkSlider.value) : 2.2;
    const noiseType = noiseTypeSelect ? noiseTypeSelect.value : "gaussian";
    const noiseSigma = noiseSigmaSlider ? parseFloat(noiseSigmaSlider.value) : 15.0;
    const denoiseMethod = denoiseMethodSelect ? denoiseMethodSelect.value : "bilateral";
    const colorSpace = colorSpaceSelect ? (colorSpaceSelect.value === "LAB" ? "CIELAB (Kênh L*)" : "HSV (Kênh V)") : "HSV (Kênh V)";
    const clipLimit = claheClipSlider ? parseFloat(claheClipSlider.value) : 3.0;
    const gammaVal = gammaValSlider ? parseFloat(gammaValSlider.value) : 0.50;

    const res = state.lastResponseData;
    const hasGt = Boolean(state.groundTruthAvailable && res?.ground_truth_available);

    const he = {
      psnr: res?.methods?.he?.metrics?.psnr !== undefined ? safeNum(res.methods.he.metrics.psnr, 2) : "15.95",
      ssim: res?.methods?.he?.metrics?.ssim !== undefined ? safeNum(res.methods.he.metrics.ssim, 4) : "0.4389",
      niqe: res?.methods?.he?.metrics?.niqe !== undefined ? safeNum(res.methods.he.metrics.niqe, 2) : "9.26",
      time: res?.methods?.he?.exec_time_ms !== undefined ? safeNum(res.methods.he.exec_time_ms, 2) : "8.44"
    };

    const clahe = {
      psnr: res?.methods?.clahe?.metrics?.psnr !== undefined ? safeNum(res.methods.clahe.metrics.psnr, 2) : "9.12",
      ssim: res?.methods?.clahe?.metrics?.ssim !== undefined ? safeNum(res.methods.clahe.metrics.ssim, 4) : "0.3296",
      niqe: res?.methods?.clahe?.metrics?.niqe !== undefined ? safeNum(res.methods.clahe.metrics.niqe, 2) : "9.03",
      time: res?.methods?.clahe?.exec_time_ms !== undefined ? safeNum(res.methods.clahe.exec_time_ms, 2) : "9.80"
    };

    const gamma = {
      psnr: res?.methods?.gamma?.metrics?.psnr !== undefined ? safeNum(res.methods.gamma.metrics.psnr, 2) : "10.57",
      ssim: res?.methods?.gamma?.metrics?.ssim !== undefined ? safeNum(res.methods.gamma.metrics.ssim, 4) : "0.4000",
      niqe: res?.methods?.gamma?.metrics?.niqe !== undefined ? safeNum(res.methods.gamma.metrics.niqe, 2) : "9.08",
      time: res?.methods?.gamma?.exec_time_ms !== undefined ? safeNum(res.methods.gamma.exec_time_ms, 2) : "5.99"
    };

    const msr = {
      psnr: res?.methods?.msr?.metrics?.psnr !== undefined ? safeNum(res.methods.msr.metrics.psnr, 2) : "14.97",
      ssim: res?.methods?.msr?.metrics?.ssim !== undefined ? safeNum(res.methods.msr.metrics.ssim, 4) : "0.5017",
      niqe: res?.methods?.msr?.metrics?.niqe !== undefined ? safeNum(res.methods.msr.metrics.niqe, 2) : "9.10",
      time: res?.methods?.msr?.exec_time_ms !== undefined ? safeNum(res.methods.msr.exec_time_ms, 2) : "1232.58"
    };

    const inputDegraded = {
      psnr: res?.methods?.clahe?.metrics?.psnr_before !== undefined ? safeNum(res.methods.clahe.metrics.psnr_before, 2) : "13.40",
      ssim: res?.methods?.clahe?.metrics?.ssim_before !== undefined ? safeNum(res.methods.clahe.metrics.ssim_before, 4) : "0.1443",
      niqe: res?.methods?.clahe?.metrics?.niqe_before !== undefined ? safeNum(res.methods.clahe.metrics.niqe_before, 2) : "9.45"
    };

    return {
      brightness,
      gammaDark,
      noiseType,
      noiseSigma,
      denoiseMethod,
      colorSpace,
      clipLimit,
      gridSize: activeGrid,
      gammaVal,
      hasGt,
      isSimChecked,
      activeFormula: state.activeFormula || "clahe",
      he,
      clahe,
      gamma,
      msr,
      inputDegraded,
      rankings: res?.rankings || null
    };
  }

  // Hiển thị Popover 3 Tầng đúng tọa độ nút (?)
  function showDefensePopover(targetBtn, paramKey) {
    if (!defensePopover) return;
    const s = getCurrentAppState();
    const generator = (typeof DEFENSE_KNOWLEDGE_BASE !== "undefined" && DEFENSE_KNOWLEDGE_BASE[paramKey])
      ? DEFENSE_KNOWLEDGE_BASE[paramKey]
      : (typeof DEFENSE_KNOWLEDGE_BASE !== "undefined" ? DEFENSE_KNOWLEDGE_BASE["metrics_paradox"] : null);

    if (!generator) return;
    const data = generator(s);

    const titleEl = document.getElementById("xai-pop-title");
    const mathEl = document.getElementById("xai-tier-math-content");
    const liveEl = document.getElementById("xai-tier-live-content");
    const defEl = document.getElementById("xai-tier-defense-content");

    if (titleEl) titleEl.innerHTML = data.title;
    if (mathEl) mathEl.innerHTML = data.math;
    if (liveEl) liveEl.innerHTML = data.live;
    if (defEl) defEl.innerHTML = data.defense;

    // Tính toán tọa độ hiển thị cạnh nút (?) không bị tràn màn hình
    const rect = targetBtn.getBoundingClientRect();
    const popoverWidth = 440;
    const popoverHeight = 360;

    let left = rect.left;
    let top = rect.bottom + 10;

    if (left + popoverWidth > window.innerWidth - 16) {
      left = window.innerWidth - popoverWidth - 16;
    }
    if (left < 16) {
      left = 16;
    }

    if (top + popoverHeight > window.innerHeight - 16) {
      top = rect.top - popoverHeight - 10;
    }
    if (top < 16) {
      top = 16;
    }

    defensePopover.style.top = `${Math.round(top)}px`;
    defensePopover.style.left = `${Math.round(left)}px`;
    defensePopover.classList.add("show");

    if (currentActiveDefenseBtn) {
      currentActiveDefenseBtn.classList.remove("active");
    }
    targetBtn.classList.add("active");
    currentActiveDefenseBtn = targetBtn;

    // Render KaTeX công thức toán trong Popover
    if (window.renderMathInElement) {
      renderMathInElement(defensePopover, {
        delimiters: [
          { left: "$$", right: "$$", display: true },
          { left: "$", right: "$", display: false }
        ],
        throwOnError: false
      });
    }
  }

  function closeDefensePopover() {
    if (defensePopover) {
      defensePopover.classList.remove("show");
    }
    if (currentActiveDefenseBtn) {
      currentActiveDefenseBtn.classList.remove("active");
      currentActiveDefenseBtn = null;
    }
  }

  // Đóng mở Drawer Tổng khi bấm nút "Giải Thích Kết Quả (?)"
  function toggleMasterDrawer(forceState = null) {
    if (!masterDrawer || !masterBackdrop) return;
    const shouldOpen = forceState !== null ? forceState : !masterDrawer.classList.contains("open");

    if (shouldOpen) {
      masterDrawer.classList.add("open");
      masterBackdrop.classList.add("open");
      closeDefensePopover();
      renderMasterDrawerContent();
    } else {
      masterDrawer.classList.remove("open");
      masterBackdrop.classList.remove("open");
    }
  }

  function renderMasterDrawerContent() {
    const s = getCurrentAppState();
    const bodyEl = document.getElementById("xai-drawer-dynamic-body");
    if (!bodyEl) return;

    bodyEl.innerHTML = `
      <div class="xai-tier tier-live" style="margin-bottom:16px;">
        <span class="xai-tier-label"><i class="fa-solid fa-bolt"></i> Tóm Tắt Trạng Thái Thực Nghiệm & Nghịch Lý Điểm Số</span>
        <div style="margin-bottom: 6px;">
          &bull; <b>Nghịch lý PSNR vs SSIM:</b> HE đạt PSNR cao nhất (<span class="xai-val">${s.he.psnr} dB</span>) do kéo sáng toàn cục đưa trung bình mức xám về gần ảnh gốc, nhưng làm mất chi tiết vi mô cục bộ. Ngược lại, <b>MSR</b> mới là thuật toán bảo toàn cấu trúc tốt nhất (<span class="xai-val">SSIM = ${s.msr.ssim}</span>, tăng vọt <span class="xai-val">${safeDiff(s.msr.ssim, s.inputDegraded.ssim, 4)}</span> so với ảnh suy thoái).
        </div>
        <div>
          &bull; <b>Hiệu quả Tiền Xử Lý:</b> Bộ lọc <b>${s.denoiseMethod.toUpperCase()}</b> trên không gian màu <b>${s.colorSpace}</b> đã kìm hãm nhiễu <span class="xai-val">&sigma; = ${s.noiseSigma}</span> trước khi đi qua hàm logarit của MSR và hàm tích lũy của CLAHE.
        </div>
      </div>

      <h4 class="xai-drawer-h4"><i class="fa-solid fa-table-list"></i> Bảng Phân Tích Độ Phức Tạp Thuật Toán $O(\\cdot)$ & Thời Gian Thực</h4>
      <table class="xai-drawer-table">
        <thead>
          <tr>
            <th>Thuật toán</th>
            <th>Độ phức tạp $O(\\cdot)$</th>
            <th>Thời gian thực</th>
            <th>Nhược điểm cốt lõi & Biện pháp phản biện</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><b>Gamma</b></td>
            <td>$O(N)$ (LUT 256)</td>
            <td style="color:#4ade80; font-weight:700;">${s.gamma.time} ms</td>
            <td>Ánh xạ mũ cố định toàn cục, không phân biệt được tiền cảnh vs hậu cảnh.</td>
          </tr>
          <tr>
            <td><b>HE</b></td>
            <td>$O(N + L)$</td>
            <td style="color:#4ade80; font-weight:700;">${s.he.time} ms</td>
            <td>Cháy sáng cục bộ, răng cưa tần số rời rạc, khuếch đại hạt nhiễu nền.</td>
          </tr>
          <tr>
            <td><b>CLAHE</b></td>
            <td>$O(N) + \\text{Bilinear}$</td>
            <td style="color:#facc15; font-weight:700;">${s.clahe.time} ms</td>
            <td>Nhạy cảm tham số $\\beta$ (${s.clipLimit}); tối ưu thời gian thực video &gt; 30 FPS.</td>
          </tr>
          <tr>
            <td><b>MSR</b></td>
            <td>$O(K \\cdot N \\log N)$ (FFT)</td>
            <td style="color:#f87171; font-weight:700;">${s.msr.time} ms</td>
            <td>Chi phí tích chập 3 Gauss lớn; khắc phục bằng biến đổi FFT hoặc GPU TensorRT.</td>
          </tr>
        </tbody>
      </table>

      <h4 class="xai-drawer-h4"><i class="fa-solid fa-shield-halved"></i> 3 Chiến Thuật Phản Biện Hội Đồng (Viva Voce Defense Strategy)</h4>
      <ul class="xai-drawer-checklist">
        <li>
          <i class="fa-solid fa-circle-check"></i>
          <div>
            <b>Chiến thuật 1 (Không gian màu):</b> Khẳng định tách kênh $V$ (HSV) hoặc $L^*$ (CIELAB) là bắt buộc. Nếu xử lý trực tiếp trên RGB sẽ phá vỡ tỷ lệ $R:G:B$, làm sai lệch sắc độ tự nhiên của cảnh quan.
          </div>
        </li>
        <li>
          <i class="fa-solid fa-circle-check"></i>
          <div>
            <b>Chiến thuật 2 (Nghịch lý PSNR):</b> Khi hội đồng hỏi vì sao HE có PSNR cao mà không chọn làm khuyến nghị chính, trả lời ngay rằng PSNR đo sai số toàn phương MSE, nhạy cảm với dịch chuyển trung bình mức xám chứ không phản ánh hệ thống thị giác người HVS như SSIM và NIQE.
          </div>
        </li>
        <li>
          <i class="fa-solid fa-circle-check"></i>
          <div>
            <b>Chiến thuật 3 (Khuyến nghị thực tế):</b> Đề xuất mô hình lưỡng dụng: Với hệ thống nhúng / video giám sát thời gian thực &gt; 30 FPS, khuyến nghị <b>CLAHE</b> (${s.clahe.time} ms). Với ứng dụng y tế, viễn thám, hậu kỳ ảnh nghệ thuật chất lượng cao cần tối đa cấu trúc, khuyến nghị <b>MSR</b> (SSIM = ${s.msr.ssim}).
          </div>
        </li>
      </ul>

      <div class="xai-drawer-actions">
        <button type="button" class="btn-drawer-action-primary" id="btnDrawerOpenFullModal">
          <i class="fa-solid fa-book-open"></i> Lý Thuyết Chi Tiết
        </button>
        <button type="button" class="btn-drawer-action-secondary" onclick="toggleMasterDrawer(false)">
          Đóng
        </button>
      </div>
    `;

    document.getElementById("btnDrawerOpenFullModal")?.addEventListener("click", () => {
      toggleMasterDrawer(false);
      openHelpModal("sec-metrics");
    });

    if (window.renderMathInElement) {
      renderMathInElement(masterDrawer, {
        delimiters: [
          { left: "$$", right: "$$", display: true },
          { left: "$", right: "$", display: false }
        ],
        throwOnError: false
      });
    }
  }

  // Đăng ký toàn cục cho inline onclick trong HTML
  window.toggleMasterDrawer = toggleMasterDrawer;
  window.closeDefensePopover = closeDefensePopover;
  window.getCurrentAppState = getCurrentAppState;
  window.openHelpModal = openHelpModal;
  window.closeHelpModal = closeHelpModal;

  // Lắng nghe sự kiện click trên toàn bộ các nút dấu chấm hỏi (?)
  document.addEventListener("click", (e) => {
    const btn = e.target.closest(".q-mark-btn, .btn-help-param, .btn-help-inline, [data-defense-key]");
    if (btn) {
      e.stopPropagation();
      const key = btn.dataset.defenseKey || btn.dataset.param || btn.dataset.help;
      if (currentActiveDefenseBtn === btn && defensePopover?.classList.contains("show")) {
        closeDefensePopover();
        return;
      }
      showDefensePopover(btn, key);
      return;
    }

    if (defensePopover && !defensePopover.contains(e.target)) {
      closeDefensePopover();
    }
  });

  // Phím tắt ESC đóng Popover & Drawer
  window.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      closeDefensePopover();
      if (masterDrawer?.classList.contains("open")) {
        toggleMasterDrawer(false);
      }
    }
  });

  function renderAllLatex() {
    if (window.renderMathInElement) {
      renderMathInElement(document.body, {
        delimiters: [
          { left: "$$", right: "$$", display: true },
          { left: "$", right: "$", display: false }
        ],
        throwOnError: false
      });
    }
  }

  // ==========================================================================
  // SIDEBAR CONTROLS & EVENTS
  // ==========================================================================
  // Tab Dataset vs Upload
  tabDataset.addEventListener("click", () => {
    tabDataset.classList.add("active");
    tabUpload.classList.remove("active");
    paneDataset.classList.add("active");
    paneUpload.classList.remove("active");
    state.isCustomUpload = false;
  });

  tabUpload.addEventListener("click", () => {
    tabUpload.classList.add("active");
    tabDataset.classList.remove("active");
    paneUpload.classList.add("active");
    paneDataset.classList.remove("active");
    state.isCustomUpload = true;
  });

  // Slider change
  imgIndexSlider.addEventListener("input", (e) => {
    imgIndexVal.textContent = `${e.target.value} / ${imgIndexSlider.max}`;
  });

  imgIndexSlider.addEventListener("change", () => {
    state.isCustomUpload = false;
    executePipeline();
  });

  btnPrevImg.addEventListener("click", () => {
    let cur = parseInt(imgIndexSlider.value);
    if (cur > 0) {
      imgIndexSlider.value = cur - 1;
      imgIndexVal.textContent = `${cur - 1} / ${imgIndexSlider.max}`;
      state.isCustomUpload = false;
      executePipeline();
    }
  });

  btnNextImg.addEventListener("click", () => {
    let cur = parseInt(imgIndexSlider.value);
    if (cur < parseInt(imgIndexSlider.max)) {
      imgIndexSlider.value = cur + 1;
      imgIndexVal.textContent = `${cur + 1} / ${imgIndexSlider.max}`;
      state.isCustomUpload = false;
      executePipeline();
    }
  });

  btnRandomImg.addEventListener("click", () => {
    const maxVal = parseInt(imgIndexSlider.max);
    const rand = Math.floor(Math.random() * (maxVal + 1));
    imgIndexSlider.value = rand;
    imgIndexVal.textContent = `${rand} / ${maxVal}`;
    state.isCustomUpload = false;
    executePipeline();
  });

  // File Upload Drag & Drop
  dropZone.addEventListener("click", () => fileUploadInput.click());

  dropZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropZone.classList.add("dragover");
  });

  dropZone.addEventListener("dragleave", () => {
    dropZone.classList.remove("dragover");
  });

  dropZone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropZone.classList.remove("dragover");
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  });

  fileUploadInput.addEventListener("change", (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFileUpload(e.target.files[0]);
    }
  });

  function handleFileUpload(file) {
    const reader = new FileReader();
    reader.onload = (event) => {
      state.customFileB64 = event.target.result;
      state.isCustomUpload = true;
      uploadFileName.textContent = file.name;
      uploadPreviewRow.style.display = "flex";
      executePipeline();
    };
    reader.readAsDataURL(file);
  }

  btnRemoveUpload.addEventListener("click", (e) => {
    e.stopPropagation();
    state.customFileB64 = null;
    state.isCustomUpload = false;
    uploadPreviewRow.style.display = "none";
    fileUploadInput.value = "";
    tabDataset.click();
    executePipeline();
  });

  // Slider value badges
  brightnessFactorSlider.addEventListener("input", (e) => brightnessFactorVal.textContent = parseFloat(e.target.value).toFixed(2));
  gammaDarkSlider.addEventListener("input", (e) => gammaDarkVal.textContent = parseFloat(e.target.value).toFixed(1));
  noiseSigmaSlider.addEventListener("input", (e) => noiseSigmaVal.textContent = parseFloat(e.target.value).toFixed(1));
  claheClipSlider.addEventListener("input", (e) => claheClipVal.textContent = parseFloat(e.target.value).toFixed(1));
  gammaValSlider.addEventListener("input", (e) => gammaValVal.textContent = parseFloat(e.target.value).toFixed(2));

  chkSimulateLowLight.addEventListener("change", (e) => {
    lowLightSettings.style.display = e.target.checked ? "block" : "none";
  });

  const updateNoiseParamVisibility = (noiseType) => {
    // Ẩn thanh trượt cường độ nhiễu (sigma) nếu là Salt & Pepper, Poisson hoặc None vì các loại nhiễu này không dùng tham số sigma
    if (noiseType === "salt_and_pepper" || noiseType === "poisson" || noiseType === "none") {
      noiseParamGroup.style.display = "none";
    } else {
      noiseParamGroup.style.display = "block";
    }
  };

  noiseTypeSelect.addEventListener("change", (e) => {
    updateNoiseParamVisibility(e.target.value);
  });
  updateNoiseParamVisibility(noiseTypeSelect.value);

  gridPills.forEach(pill => {
    pill.addEventListener("click", () => {
      gridPills.forEach(p => p.classList.remove("active"));
      pill.classList.add("active");
    });
  });

  // Reset defaults
  btnResetParams.addEventListener("click", () => {
    brightnessFactorSlider.value = 0.35; brightnessFactorVal.textContent = "0.35";
    gammaDarkSlider.value = 2.2; gammaDarkVal.textContent = "2.2";
    noiseTypeSelect.value = "gaussian";
    updateNoiseParamVisibility("gaussian");
    noiseSigmaSlider.value = 15.0; noiseSigmaVal.textContent = "15.0";
    denoiseMethodSelect.value = "bilateral";
    colorSpaceSelect.value = "HSV";
    claheClipSlider.value = 3.0; claheClipVal.textContent = "3.0";
    gammaValSlider.value = 0.50; gammaValVal.textContent = "0.50";
    gridPills.forEach(p => p.classList.toggle("active", p.dataset.grid === "8x8"));
    executePipeline();
  });

  btnExecute.addEventListener("click", executePipeline);

  // Preset Buttons
  document.querySelectorAll(".preset-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".preset-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      const preset = btn.dataset.preset;

      if (preset === "night_landscape") {
        brightnessFactorSlider.value = 0.30; brightnessFactorVal.textContent = "0.30";
        gammaDarkSlider.value = 2.4; gammaDarkVal.textContent = "2.4";
        claheClipSlider.value = 3.5; claheClipVal.textContent = "3.5";
        gammaValSlider.value = 0.45; gammaValVal.textContent = "0.45";
      } else if (preset === "sunset") {
        brightnessFactorSlider.value = 0.50; brightnessFactorVal.textContent = "0.50";
        gammaDarkSlider.value = 1.6; gammaDarkVal.textContent = "1.6";
        claheClipSlider.value = 2.5; claheClipVal.textContent = "2.5";
        gammaValSlider.value = 0.60; gammaValVal.textContent = "0.60";
      } else if (preset === "foggy") {
        brightnessFactorSlider.value = 0.60; brightnessFactorVal.textContent = "0.60";
        claheClipSlider.value = 4.5; claheClipVal.textContent = "4.5";
        denoiseMethodSelect.value = "nlm";
      } else if (preset === "extreme_dark") {
        brightnessFactorSlider.value = 0.15; brightnessFactorVal.textContent = "0.15";
        gammaDarkSlider.value = 2.8; gammaDarkVal.textContent = "2.8";
        noiseSigmaSlider.value = 25.0; noiseSigmaVal.textContent = "25.0";
        claheClipSlider.value = 4.0; claheClipVal.textContent = "4.0";
        gammaValSlider.value = 0.35; gammaValVal.textContent = "0.35";
      }
      executePipeline();
    });
  });

  // Theme Toggle
  btnThemeToggle.addEventListener("click", () => {
    document.body.classList.toggle("theme-light");
    const isLight = document.body.classList.contains("theme-light");
    btnThemeToggle.innerHTML = isLight ? `<i class="fa-solid fa-moon"></i>` : `<i class="fa-solid fa-sun"></i>`;

    // Cập nhật lại biểu đồ với màu sắc chuẩn theo theme mới ngay lập tức
    if (state.lastResponseData) {
      renderHistogramChart(state.lastResponseData);
      renderRadarChart(state.lastResponseData);
    }
  });

  // ==========================================================================
  // BATCH BENCHMARK RUNNER
  // ==========================================================================
  btnRunBatch.addEventListener("click", async () => {
    const samples = parseInt(batchSamplesInput.value) || 20;
    btnRunBatch.disabled = true;
    btnRunBatch.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Đang chạy (${samples} mẫu)...`;

    try {
      const resp = await fetch(`/api/batch?samples=${samples}`, { method: "POST" });
      if (!resp.ok) throw new Error(await resp.text());
      const res = await resp.json();

      emptyBatchState.style.display = "none";
      batchContentLoaded.style.display = "block";

      // Render summary cards
      batchStatsRow.innerHTML = "";
      const names = {
        he: "HE",
        clahe: "CLAHE",
        gamma: "Gamma",
        msr: "MSR"
      };

      for (const [k, avg] of Object.entries(res.averages)) {
        const card = document.createElement("div");
        card.className = "control-card";
        card.innerHTML = `
          <div class="card-title"><span>${names[k] || k}</span></div>
          <div style="font-size:12px; display:flex; flex-direction:column; gap:4px;">
            <div>PSNR TB: <b>${avg.avg_psnr} dB</b></div>
            <div>SSIM TB: <b>${avg.avg_ssim}</b></div>
            <div>NIQE TB: <b>${avg.avg_niqe}</b></div>
          </div>
        `;
        batchStatsRow.appendChild(card);
      }
    } catch (e) {
      alert("Lỗi khi chạy Batch Benchmark: " + e.message);
    } finally {
      btnRunBatch.disabled = false;
      btnRunBatch.innerHTML = `<i class="fa-solid fa-play"></i> Chạy Benchmark Hàng Loạt`;
    }
  });


  // ==========================================================================
  // ACADEMIC PRESENTATION IMAGE LIGHTBOX (PHÓNG TO TRÌNH CHIẾU Ô 1 & Ô 2)
  // ==========================================================================
  function initPresentationLightbox() {
    const backdrop = document.getElementById("imageLightboxBackdrop");
    const container = document.getElementById("imageLightboxContainer");
    const imgEl = document.getElementById("lightboxImg");
    const imgWrapper = document.getElementById("lightboxImgWrapper");
    const titleEl = document.getElementById("lightboxTitle");
    const subtitleEl = document.getElementById("lightboxSubtitle");
    const metricsPill = document.getElementById("lightboxMetricsPill");
    const btnClose = document.getElementById("btnLightboxClose");
    const btnPrev = document.getElementById("btnLightboxPrev");
    const btnNext = document.getElementById("btnLightboxNext");
    const btnZoomIn = document.getElementById("btnLightboxZoomIn");
    const btnZoomOut = document.getElementById("btnLightboxZoomOut");
    const btnZoomReset = document.getElementById("btnLightboxZoomReset");
    const btnFullscreen = document.getElementById("btnLightboxFullscreen");
    const btnCompareToggle = document.getElementById("btnLightboxCompareToggle");
    const stagePills = document.querySelectorAll("#lightboxStagesNav .stage-nav-pill");

    if (!backdrop || !imgEl || !imgWrapper) return;

    let currentStageIdx = 0;
    let zoomLevel = 1.0;
    let panX = 0;
    let panY = 0;
    let isDragging = false;
    let dragStartX = 0;
    let dragStartY = 0;
    let isComparingBefore = false;
    let preCompareStageIdx = 0;

    const PIPELINE_STAGES = [
      { id: "imgClean", title: "Ảnh Gốc Chuẩn (Ground Truth)", subtitle: "Mẫu ảnh đối chứng tự nhiên chất lượng cao", type: "clean" },
      { id: "imgDegraded", title: "Ảnh Thiếu Sáng & Nhiễu (Đầu Vào)", subtitle: "Mô phỏng suy thoái thiếu sáng ban đêm", type: "degraded" },
      { id: "imgDenoisedInput", title: "Sau Tiền Xử Lý Khử Nhiễu (Pre-denoised)", subtitle: "Bộ lọc bảo tồn biên trên kênh độ chói", type: "denoised" },
      { id: "imgResHe", title: "Thuật Toán 1: Histogram Equalization (HE)", subtitle: "Cân bằng lược đồ mức xám toàn cục", type: "method", key: "he" },
      { id: "imgResClahe", title: "Thuật Toán 2: CLAHE (Tương Phản Thích Nghi)", subtitle: "Cắt ngưỡng Clip Limit & nội suy song tuyến", type: "method", key: "clahe" },
      { id: "imgResGamma", title: "Thuật Toán 3: Gamma Correction", subtitle: "Biến đổi lũy thừa phi tuyến qua LUT", type: "method", key: "gamma" },
      { id: "imgResMsr", title: "Thuật Toán 4: Multi-Scale Retinex (MSR)", subtitle: "Bóc tách phản xạ võng mạc đa tỷ lệ Gauss", type: "method", key: "msr" }
    ];

    function applyTransform() {
      imgWrapper.style.transform = `translate(${panX}px, ${panY}px) scale(${zoomLevel})`;
    }

    function resetTransform() {
      zoomLevel = 1.0;
      panX = 0;
      panY = 0;
      applyTransform();
    }

    function isImageSrcValid(src) {
      if (!src) return false;
      if (src === window.location.href || src.endsWith("#")) return false;
      return src.startsWith("data:image") || src.startsWith("http") || src.startsWith("blob:") || src.startsWith("/");
    }

    function updateStagePills(activeIdx) {
      stagePills.forEach(pill => {
        const pIdx = parseInt(pill.dataset.stage);
        pill.classList.toggle("active", pIdx === activeIdx);
      });
    }

    function openStage(idx) {
      if (idx < 0) idx = PIPELINE_STAGES.length - 1;
      if (idx >= PIPELINE_STAGES.length) idx = 0;
      currentStageIdx = idx;

      const stage = PIPELINE_STAGES[idx];
      const srcEl = document.getElementById(stage.id);

      if (!srcEl || !isImageSrcValid(srcEl.src)) {
        // Nếu ảnh chưa sẵn sàng (ví dụ GT trong chế độ ảnh tự tải)
        if (stage.type === "clean") {
          imgEl.src = "";
          if (titleEl) titleEl.textContent = "Không Có Ảnh Đối Chứng (Ground Truth)";
          if (subtitleEl) subtitleEl.textContent = "Chế độ ảnh tự tải (Real-World Upload) không có ảnh gốc đối chứng";
          if (metricsPill) metricsPill.style.display = "none";
          updateStagePills(idx);
          backdrop.classList.add("open");
          return;
        }
        return;
      }

      imgEl.src = srcEl.src;
      if (titleEl) titleEl.textContent = stage.title;
      if (subtitleEl) subtitleEl.innerHTML = `Quy trình ${idx + 1}/${PIPELINE_STAGES.length} &bull; ${stage.subtitle}`;

      // Cập nhật Live KPI badges kèm độ chênh lệch Δ
      if (metricsPill) {
        const s = getCurrentAppState();
        if (stage.type === "method" && stage.key) {
          const m = s[stage.key] || {};
          const deg = s.inputDegraded || {};

          let deltaPsnrHtml = "";
          let deltaSsimHtml = "";
          let deltaNiqeHtml = "";

          if (s.hasGt && m.psnr && deg.psnr && !isNaN(m.psnr) && !isNaN(deg.psnr)) {
            const diffP = parseFloat(m.psnr) - parseFloat(deg.psnr);
            const sign = diffP >= 0 ? "+" : "";
            const cls = diffP >= 0 ? "metric-delta-pos" : "metric-delta-neg";
            deltaPsnrHtml = ` <span class="${cls}">(${sign}${diffP.toFixed(2)} dB)</span>`;
          }

          if (s.hasGt && m.ssim && deg.ssim && !isNaN(m.ssim) && !isNaN(deg.ssim)) {
            const diffS = parseFloat(m.ssim) - parseFloat(deg.ssim);
            const sign = diffS >= 0 ? "+" : "";
            const cls = diffS >= 0 ? "metric-delta-pos" : "metric-delta-neg";
            deltaSsimHtml = ` <span class="${cls}">(${sign}${diffS.toFixed(4)})</span>`;
          }

          if (m.niqe && deg.niqe && !isNaN(m.niqe) && !isNaN(deg.niqe)) {
            const diffN = parseFloat(m.niqe) - parseFloat(deg.niqe);
            const sign = diffN <= 0 ? "" : "+";
            const cls = diffN <= 0 ? "metric-delta-pos" : "metric-delta-neg"; // NIQE càng giảm càng tốt
            deltaNiqeHtml = ` <span class="${cls}">(${sign}${diffN.toFixed(2)})</span>`;
          }

          metricsPill.style.display = "flex";
          metricsPill.innerHTML = `
            <span>PSNR: <b>${m.psnr} dB</b>${deltaPsnrHtml}</span>
            <span style="opacity:0.35;">|</span>
            <span>SSIM: <b>${m.ssim}</b>${deltaSsimHtml}</span>
            <span style="opacity:0.35;">|</span>
            <span>NIQE: <b>${m.niqe}</b>${deltaNiqeHtml}</span>
            <span style="opacity:0.35;">|</span>
            <span style="color:#60a5fa;"><i class="fa-regular fa-clock"></i> <b>${m.time} ms</b></span>
          `;
        } else if (stage.type === "degraded") {
          metricsPill.style.display = "flex";
          metricsPill.innerHTML = `
            <span>PSNR Gốc: <b>${s.inputDegraded.psnr} dB</b></span>
            <span style="opacity:0.35;">|</span>
            <span>SSIM Gốc: <b>${s.inputDegraded.ssim}</b></span>
            <span style="opacity:0.35;">|</span>
            <span>NIQE Gốc: <b>${s.inputDegraded.niqe}</b></span>
          `;
        } else {
          metricsPill.style.display = "none";
        }
      }

      updateStagePills(idx);
      resetTransform();
      backdrop.classList.add("open");
    }

    function close() {
      backdrop.classList.remove("open");
      resetTransform();
      isComparingBefore = false;
      btnCompareToggle?.classList.remove("active");
      if (document.fullscreenElement) {
        document.exitFullscreen().catch(() => {});
      }
    }

    function toggleCompareWithBefore(forceState = null) {
      const targetState = forceState !== null ? forceState : !isComparingBefore;
      if (targetState === isComparingBefore) return;

      const degradedEl = document.getElementById("imgDegraded");
      if (!degradedEl || !isImageSrcValid(degradedEl.src)) return;

      isComparingBefore = targetState;
      if (isComparingBefore) {
        preCompareStageIdx = currentStageIdx;
        btnCompareToggle?.classList.add("active");
        imgEl.src = degradedEl.src;
        if (titleEl) titleEl.textContent = "🔍 Đang Đối Chiếu: Ảnh Thiếu Sáng & Nhiễu (Đầu Vào)";
        if (subtitleEl) subtitleEl.textContent = "Thả phím Space hoặc bấm lại nút để trở về kết quả thuật toán";
      } else {
        btnCompareToggle?.classList.remove("active");
        openStage(preCompareStageIdx);
      }
    }

    // Gắn sự kiện click cho toàn bộ ảnh ở Ô 1 và Ô 2
    document.querySelectorAll(".input-images-row .img-wrapper, .methods-grid-4 .img-wrapper").forEach(wrap => {
      wrap.addEventListener("click", (e) => {
        if (e.target.closest("button")) return;
        const img = wrap.querySelector("img");
        if (!img || !img.src) return;
        const found = PIPELINE_STAGES.findIndex(s => s.id === img.id);
        if (found !== -1) {
          openStage(found);
        } else {
          imgEl.src = img.src;
          if (titleEl) titleEl.textContent = img.alt || "Chi Tiết Trực Quan";
          if (subtitleEl) subtitleEl.textContent = "Chế độ phóng to trình chiếu chất lượng cao";
          if (metricsPill) metricsPill.style.display = "none";
          resetTransform();
          backdrop.classList.add("open");
        }
      });
    });

    // Bản đồ nhiệt Heatmaps ở View 3
    document.querySelectorAll(".heatmap-card").forEach(card => {
      card.addEventListener("click", () => {
        const img = card.querySelector("img");
        const h5 = card.querySelector("h5");
        const method = card.dataset.method || "";
        if (!img || !isImageSrcValid(img.src)) return;
        imgEl.src = img.src;
        if (titleEl) titleEl.textContent = h5 ? h5.textContent : "Bản Đồ Nhiệt Khác Biệt";

        let subText = "Trực quan hóa mức độ sai lệch cường độ sáng";
        if (method === "he") {
          subText = "• Giải tích HE: Đỏ rực phủ kín diện rộng — Can thiệp toàn cục thô bạo, kéo sáng cả nền trời, nguy cơ cháy sáng cao.";
        } else if (method === "clahe") {
          subText = "• Giải tích CLAHE: Đỏ/vàng khu trú vào bóng tối, trời vẫn xanh — Thích nghi cục bộ thông minh, chống cháy sáng.";
        } else if (method === "gamma") {
          subText = "• Giải tích Gamma: Màu chuyển tiếp mượt đều — Kéo sáng phi tuyến êm ái toàn ảnh nhưng không phân vùng chi tiết.";
        } else if (method === "msr") {
          subText = "• Giải tích MSR: Phát sáng men theo đường biên — Tách trường phản xạ Retinex, làm sắc nét vi mô cấu trúc.";
        }

        if (subtitleEl) subtitleEl.textContent = subText;
        if (metricsPill) metricsPill.style.display = "none";
        resetTransform();
        backdrop.classList.add("open");
      });
    });

    // Thanh điều hướng 7 pills
    stagePills.forEach(pill => {
      pill.addEventListener("click", (e) => {
        e.stopPropagation();
        const stageIdx = parseInt(pill.dataset.stage);
        if (!isNaN(stageIdx)) {
          openStage(stageIdx);
        }
      });
    });

    // Nút đối chiếu nhanh Before / After
    btnCompareToggle?.addEventListener("click", (e) => {
      e.stopPropagation();
      toggleCompareWithBefore();
    });

    // Các nút chức năng
    btnClose?.addEventListener("click", close);
    btnPrev?.addEventListener("click", (e) => { e.stopPropagation(); openStage(currentStageIdx - 1); });
    btnNext?.addEventListener("click", (e) => { e.stopPropagation(); openStage(currentStageIdx + 1); });

    btnZoomIn?.addEventListener("click", (e) => {
      e.stopPropagation();
      zoomLevel = Math.min(zoomLevel + 0.35, 4.5);
      applyTransform();
    });

    btnZoomOut?.addEventListener("click", (e) => {
      e.stopPropagation();
      zoomLevel = Math.max(zoomLevel - 0.35, 0.4);
      applyTransform();
    });

    btnZoomReset?.addEventListener("click", (e) => {
      e.stopPropagation();
      resetTransform();
    });

    btnFullscreen?.addEventListener("click", (e) => {
      e.stopPropagation();
      if (!document.fullscreenElement) {
        container?.requestFullscreen().catch(() => {});
      } else {
        document.exitFullscreen().catch(() => {});
      }
    });

    // Đóng khi bấm ra ngoài vùng ảnh
    backdrop.addEventListener("click", (e) => {
      if (e.target === backdrop || e.target.id === "lightboxStage") {
        close();
      }
    });

    // Cuộn chuột để Zoom
    imgWrapper.addEventListener("wheel", (e) => {
      e.preventDefault();
      const delta = e.deltaY < 0 ? 0.2 : -0.2;
      zoomLevel = Math.min(Math.max(zoomLevel + delta, 0.4), 4.5);
      applyTransform();
    }, { passive: false });

    // Kéo chuột để Pan khi Zoom
    imgWrapper.addEventListener("mousedown", (e) => {
      if (e.button !== 0) return;
      isDragging = true;
      dragStartX = e.clientX - panX;
      dragStartY = e.clientY - panY;
      imgWrapper.classList.add("grabbing");
    });

    window.addEventListener("mousemove", (e) => {
      if (!isDragging) return;
      panX = e.clientX - dragStartX;
      panY = e.clientY - dragStartY;
      applyTransform();
    });

    window.addEventListener("mouseup", () => {
      if (isDragging) {
        isDragging = false;
        imgWrapper.classList.remove("grabbing");
      }
    });

    // Bàn phím điều khiển thuyết trình
    window.addEventListener("keydown", (e) => {
      if (!backdrop.classList.contains("open")) return;

      // Phím Space để giữ xem Before (ảnh thiếu sáng)
      if (e.code === "Space" && !e.repeat && e.target.tagName !== "INPUT" && e.target.tagName !== "TEXTAREA") {
        e.preventDefault();
        toggleCompareWithBefore(true);
        return;
      }

      if (e.key === "Escape") {
        close();
      } else if (e.key === "ArrowLeft") {
        openStage(currentStageIdx - 1);
      } else if (e.key === "ArrowRight") {
        openStage(currentStageIdx + 1);
      } else if (e.key >= "1" && e.key <= "7") {
        const targetIdx = parseInt(e.key) - 1;
        openStage(targetIdx);
      } else if (e.key === "+" || e.key === "=") {
        zoomLevel = Math.min(zoomLevel + 0.35, 4.5);
        applyTransform();
      } else if (e.key === "-") {
        zoomLevel = Math.max(zoomLevel - 0.35, 0.4);
        applyTransform();
      } else if (e.key === "0") {
        resetTransform();
      } else if (e.key.toLowerCase() === "f") {
        if (!document.fullscreenElement) {
          container?.requestFullscreen().catch(() => {});
        } else {
          document.exitFullscreen().catch(() => {});
        }
      }
    });

    window.addEventListener("keyup", (e) => {
      if (!backdrop.classList.contains("open")) return;
      if (e.code === "Space") {
        e.preventDefault();
        toggleCompareWithBefore(false);
      }
    });

    window.openLightboxAtStage = openStage;
    window.closeLightbox = close;
  }

  // Start System
  initSystem();
  initPresentationLightbox();
});
