// static/js/auth.js
// Forgot Password flow: request OTP, verify OTP, reset password
// - waits for DOMContentLoaded
// - reads csrftoken cookie and sends X-CSRFToken header
// - detects whether input is email vs username
// - logs useful info to console for debugging

(function () {
  // helper: read cookie (Django csrftoken)
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + "=")) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  // Read CSRF token once at top-level so postJSON can access it
  const csrftoken = getCookie("csrftoken");

  // simple heuristic for email-like input
  function looksLikeEmail(s) {
    return typeof s === "string" && s.includes("@");
  }

  // small helper to safely query element value
  function elValue(id) {
    const e = document.getElementById(id);
    return e ? (e.value || "").trim() : "";
  }

  // POST JSON helper with CSRF
  async function postJSON(url, data) {
    try {
      const res = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrftoken || ""
        },
        body: JSON.stringify(data)
      });
      const json = await res.json().catch(() => ({}));
      return { status: res.status, json };
    } catch (err) {
      console.error("Network error while POST to", url, err);
      return { status: 0, json: { detail: "Network error" } };
    }
  }

  // DOM ready
  document.addEventListener("DOMContentLoaded", function () {
    try {
      if (!csrftoken) console.warn("CSRF token not found. AJAX POSTs may be rejected.");

      // Endpoints (match your LMS_users/urls.py)
      const REQ_URL = "/auth/api/auth/request-reset/";
      const VERIFY_URL = "/auth/api/auth/verify-otp/";
      const RESET_URL = "/auth/api/auth/reset-password/";

      // DOM elements (may be null on pages without modal)
      const requestBtn = document.getElementById("fp-request-btn");
      const verifyBtn  = document.getElementById("fp-verify-btn");
      const resendBtn  = document.getElementById("fp-resend-btn");
      const resetBtn   = document.getElementById("fp-reset-btn");

      const alertBox = document.getElementById("fp-alert");
      const userDisplay = document.getElementById("fp-user-display");

      function showAlert(message, type = "info") {
        if (alertBox) {
          alertBox.innerHTML = `<div class="alert alert-${type}">${message}</div>`;
        } else {
          console.log("FP:", message);
        }
      }

      let lastResetToken = null;
      let currentUsername = null;

      // Request OTP handler
      if (requestBtn) {
        requestBtn.addEventListener("click", async function () {
          const raw = elValue("fp-username");
          if (!raw) { showAlert("Enter username or email", "warning"); return; }
          const usernameOrEmail = raw;
          showAlert("Sending OTP...", "info");

          const payload = looksLikeEmail(usernameOrEmail)
            ? { username: "", email: usernameOrEmail }
            : { username: usernameOrEmail, email: "" };

          const { status, json } = await postJSON(REQ_URL, payload);
          console.log("Request OTP response:", status, json);

          if (status === 200) {
            showAlert(json.detail || "OTP sent", "success");
            // show verify step
            const reqStep = document.getElementById("fp-step-request");
            const verStep = document.getElementById("fp-step-verify");
            if (reqStep && verStep) {
              reqStep.classList.add("d-none");
              verStep.classList.remove("d-none");
            }
            currentUsername = usernameOrEmail;
          } else {
            showAlert(json.detail || "Error sending OTP", "danger");
          }
        });
      } else {
        console.log("fp-request-btn not found on page.");
      }

      // Verify OTP handler
      if (verifyBtn) {
        verifyBtn.addEventListener("click", async function () {
          const otp = elValue("fp-otp");
          if (!otp) { showAlert("Enter OTP", "warning"); return; }
          if (!currentUsername) { showAlert("Username missing, restart flow", "warning"); return; }
          showAlert("Verifying OTP...", "info");
          const { status, json } = await postJSON(VERIFY_URL, { username: currentUsername, otp: otp });
          console.log("Verify OTP response:", status, json);
          if (status === 200) {
            lastResetToken = json.reset_token;
            showAlert("OTP verified. Please set a new password.", "success");
            // show reset step
            const verStep = document.getElementById("fp-step-verify");
            const resetStep = document.getElementById("fp-step-reset");
            if (verStep && resetStep) {
              verStep.classList.add("d-none");
              resetStep.classList.remove("d-none");
            }
            if (userDisplay) userDisplay.textContent = currentUsername;
          } else {
            showAlert(json.detail || "OTP invalid or expired", "danger");
          }
        });
      }

      // Resend OTP handler
      if (resendBtn) {
        resendBtn.addEventListener("click", async function () {
          if (!currentUsername) { showAlert("No username to resend for", "warning"); return; }
          showAlert("Resending OTP...", "info");
          const payload = looksLikeEmail(currentUsername)
            ? { username: "", email: currentUsername }
            : { username: currentUsername, email: "" };
          const { status, json } = await postJSON(REQ_URL, payload);
          console.log("Resend OTP response:", status, json);
          if (status === 200) {
            showAlert("OTP resent", "success");
          } else {
            showAlert(json.detail || "Error resending OTP", "danger");
          }
        });
      }

      // Reset password handler
      if (resetBtn) {
        resetBtn.addEventListener("click", async function () {
          const p1 = elValue("fp-new-password");
          const p2 = elValue("fp-confirm-password");
          if (!p1 || !p2) { showAlert("Fill both password fields", "warning"); return; }
          if (p1 !== p2) { showAlert("Passwords do not match", "warning"); return; }
          if (!lastResetToken || !currentUsername) { showAlert("Missing token, restart flow", "warning"); return; }

          showAlert("Updating password...", "info");
          const { status, json } = await postJSON(RESET_URL, {
            username: currentUsername,
            reset_token: lastResetToken,
            new_password: p1
          });
          console.log("Reset password response:", status, json);
          if (status === 200) {
            showAlert(json.detail || "Password updated", "success");
            // close modal after short delay
            setTimeout(() => {
              const modalEl = document.getElementById("forgotModal");
              if (modalEl) {
                const bsModal = bootstrap.Modal.getInstance(modalEl);
                bsModal && bsModal.hide();
              }
            }, 900);
          } else {
            showAlert(json.detail || "Error updating password", "danger");
          }
        });
      }

      console.log("auth.js initialized (Forgot Password handlers)");
    } catch (err) {
      console.error("auth.js initialization error:", err);
    }
  });
})();
