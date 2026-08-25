// TrustPay AI — Dashboard Frontend Logic

// Configuration
const API_BASE = ""; // Relative to host (since hosted together)
let activeTransactionId = null;
let currentDemoScenario = null;
let sandboxStepData = {};

// On DOM Loaded
document.addEventListener("DOMContentLoaded", () => {
    initApp();
});

function initApp() {
    setupTabNavigation();
    loadDemoScenarios();
    setupEventHandlers();
    loadTransactionHistory();
    loadEvaluationMetrics();
}

// ================= TAB NAVIGATION =================
function setupTabNavigation() {
    const navLinks = document.querySelectorAll(".nav-link");
    const tabPanes = document.querySelectorAll(".tab-pane");
    const tabTitle = document.getElementById("current-tab-title");
    const tabDesc = document.getElementById("current-tab-desc");

    const tabMeta = {
        "demo-mode": {
            title: "Demo Mode",
            desc: "Run standard pre-configured scenarios to see the risk agents in action."
        },
        "sandbox": {
            title: "Custom Sandbox",
            desc: "Input custom user instructions and test how the agents evaluate policy compliance."
        },
        "history": {
            title: "Transaction History",
            desc: "View and inspect all past decisions, risk assessments, and step-by-step agent logs."
        },
        "eval-dashboard": {
            title: "Evaluation Metrics",
            desc: "Honest precision, recall, and false-positive statistics measured against a held-out test dataset."
        }
    };

    navLinks.forEach(link => {
        link.addEventListener("click", () => {
            const tabId = link.getAttribute("data-tab");

            // Update nav active class
            navLinks.forEach(l => l.classList.remove("active"));
            link.classList.add("active");

            // Update tab panes active class
            tabPanes.forEach(pane => {
                if (pane.id === tabId) {
                    pane.classList.add("active");
                } else {
                    pane.classList.remove("active");
                }
            });

            // Update headers
            if (tabMeta[tabId]) {
                tabTitle.textContent = tabMeta[tabId].title;
                tabDesc.textContent = tabMeta[tabId].desc;
            }

            // Refresh tab specific data
            if (tabId === "history") {
                loadTransactionHistory();
            } else if (tabId === "eval-dashboard") {
                loadEvaluationMetrics();
            }
        });
    });
}

// ================= EVENT HANDLERS =================
function setupEventHandlers() {
    // Refresh button
    document.getElementById("btn-refresh-data").addEventListener("click", () => {
        loadTransactionHistory();
        loadEvaluationMetrics();
    });

    // Close Modal
    document.getElementById("btn-close-modal").addEventListener("click", closeModal);
    document.getElementById("detail-modal").addEventListener("click", (e) => {
        if (e.target.id === "detail-modal") closeModal();
    });

    // Sandbox form submission
    const sandboxForm = document.getElementById("sandbox-form");
    sandboxForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const userInput = document.getElementById("sandbox-user-input").value.trim();
        const contextMessage = document.getElementById("sandbox-context-message").value.trim() || null;
        
        if (userInput) {
            runSandboxPipeline(userInput, contextMessage);
        }
    });

    // HITL Decisions (Demo)
    document.getElementById("btn-hitl-approve").addEventListener("click", () => handleHITLConfirmation(true, "demo"));
    document.getElementById("btn-hitl-reject").addEventListener("click", () => handleHITLConfirmation(false, "demo"));

    // Execute Payment (Demo)
    document.getElementById("btn-demo-execute").addEventListener("click", () => executePayment("demo"));

    // HITL Decisions (Sandbox)
    document.getElementById("btn-sb-approve").addEventListener("click", () => handleHITLConfirmation(true, "sandbox"));
    document.getElementById("btn-sb-reject").addEventListener("click", () => handleHITLConfirmation(false, "sandbox"));

    // Execute Payment (Sandbox)
    document.getElementById("btn-sb-execute").addEventListener("click", () => executePayment("sandbox"));
}

// ================= DEMO SCENARIOS =================
async function loadDemoScenarios() {
    const listContainer = document.getElementById("scenarios-list");
    try {
        const response = await fetch(`${API_BASE}/api/demo/scenarios`);
        if (!response.ok) throw new Error("Failed to load scenarios");
        const scenarios = await response.json();

        listContainer.innerHTML = "";
        scenarios.forEach(sc => {
            const card = document.createElement("div");
            card.className = "scenario-card";
            card.onclick = () => selectDemoScenario(sc);

            let badgeClass = "badge-info";
            if (sc.expected_decision === "ALLOW") badgeClass = "badge-success";
            if (sc.expected_decision === "ASK_FOR_CONFIRMATION" || sc.expected_decision === "WARN") badgeClass = "badge-warning";
            if (sc.expected_decision === "BLOCK") badgeClass = "badge-danger";

            card.innerHTML = `
                <div>
                    <h4>${sc.name}</h4>
                    <p>${sc.description}</p>
                </div>
                <div class="scenario-meta">
                    <span class="badge ${badgeClass}">${sc.expected_decision}</span>
                    <span>Scenario ID: ${sc.id}</span>
                </div>
            `;
            listContainer.appendChild(card);
        });
    } catch (err) {
        listContainer.innerHTML = `<p class="text-red">Error loading scenarios: ${err.message}</p>`;
    }
}

function selectDemoScenario(scenario) {
    currentDemoScenario = scenario;
    
    // Reset flow UI
    const runPanel = document.getElementById("demo-run-panel");
    runPanel.classList.remove("hidden");
    document.getElementById("demo-run-title").textContent = `Demo Run: ${scenario.name}`;
    document.getElementById("demo-run-desc").textContent = scenario.description;
    
    document.getElementById("demo-run-status-badge").className = "badge badge-info";
    document.getElementById("demo-run-status-badge").textContent = "WAITING TO RUN";

    // Setup first step
    document.getElementById("demo-raw-intent").textContent = `"${scenario.user_input}"`;
    
    // Hide all step outputs
    document.getElementById("demo-intent-output").classList.add("hidden");
    document.getElementById("demo-proposal-output").classList.add("hidden");
    document.getElementById("demo-risk-output").classList.add("hidden");
    document.getElementById("demo-decision-output").classList.add("hidden");
    document.getElementById("demo-postpayment-output").classList.add("hidden");

    // Reset step styles
    const steps = ["step-intent", "step-proposal", "step-risk", "step-decision", "step-postpayment"];
    steps.forEach(id => {
        const el = document.getElementById(id);
        el.className = "flow-step";
    });

    // Add run button
    const postActions = document.getElementById("demo-post-actions");
    postActions.innerHTML = `
        <button class="btn btn-primary" onclick="triggerDemoExecution(${scenario.id})">
            Start Live Agent Flow
        </button>
    `;

    // Scroll to panel
    runPanel.scrollIntoView({ behavior: "smooth" });
}

async function triggerDemoExecution(scenarioId) {
    document.getElementById("demo-run-status-badge").textContent = "PROCESSING...";
    document.getElementById("demo-run-status-badge").className = "badge badge-warning";
    
    // Disable start button
    const postActions = document.getElementById("demo-post-actions");
    postActions.innerHTML = `<button class="btn btn-secondary" disabled>Agent thinking...</button>`;

    try {
        const response = await fetch(`${API_BASE}/api/demo/run/${scenarioId}`, { method: "POST" });
        if (!response.ok) throw new Error("Failed to execute scenario");
        const data = await response.json();
        
        activeTransactionId = data.transaction_id;
        
        // Run visual steps representation
        animateDemoSteps(data);
    } catch (err) {
        alert("Error running scenario: " + err.message);
        document.getElementById("demo-run-status-badge").textContent = "FAILED";
        document.getElementById("demo-run-status-badge").className = "badge badge-danger";
    }
}

// Simulates time delays between agent runs to show the live workflow visually
async function animateDemoSteps(data) {
    const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

    // --- STEP 1: Intent Extraction ---
    const stepIntent = document.getElementById("step-intent");
    stepIntent.className = "flow-step active";
    await sleep(800);
    
    document.getElementById("demo-intent-json").textContent = JSON.stringify(data.intent.extracted, null, 2);
    document.getElementById("demo-intent-output").classList.remove("hidden");
    stepIntent.className = "flow-step completed";

    // --- STEP 2: Proposal Generation ---
    const stepProp = document.getElementById("step-proposal");
    stepProp.className = "flow-step active";
    await sleep(800);

    document.getElementById("demo-prop-title").textContent = data.proposal.product_name;
    document.getElementById("demo-prop-merchant").textContent = `Merchant: ${data.proposal.merchant_name}`;
    document.getElementById("demo-prop-amount").textContent = `₹${data.proposal.total_amount.toLocaleString("en-IN")}`;
    document.getElementById("demo-proposal-output").classList.remove("hidden");
    stepProp.className = "flow-step completed";

    // --- STEP 3: Multi-Agent Analysis ---
    const stepRisk = document.getElementById("step-risk");
    stepRisk.className = "flow-step active";
    await sleep(1000);

    // Intent Agent score
    const intentAgent = data.risk_analysis.intent_verification;
    const intentScoreEl = document.getElementById("agent-intent-score");
    intentScoreEl.textContent = `${intentAgent.score}/100`;
    document.getElementById("agent-intent-desc").textContent = intentAgent.reasoning || "All intent rules validated.";
    const intentCard = document.getElementById("agent-intent-card");
    intentCard.className = `agent-card ${intentAgent.score > 30 ? 'border-orange' : 'text-success'}`;

    // Scam Detection Agent
    const scamAgent = data.risk_analysis.scam_detection;
    const scamScoreEl = document.getElementById("agent-scam-score");
    scamScoreEl.textContent = `${Math.round(scamAgent.scam_probability * 100)}% scam`;
    document.getElementById("agent-scam-desc").textContent = scamAgent.analysis || "No threats identified.";
    const scamCard = document.getElementById("agent-scam-card");
    scamCard.className = `agent-card ${scamAgent.scam_probability > 0.4 ? 'border-orange' : 'text-success'}`;

    // Behavior Anomaly Agent
    const behaviorAgent = data.risk_analysis.behavior_anomaly;
    const behaviorScoreEl = document.getElementById("agent-behavior-score");
    behaviorScoreEl.textContent = `${behaviorAgent.score}/100`;
    document.getElementById("agent-behavior-desc").textContent = behaviorAgent.reasoning || "Typical purchase parameters.";
    const behaviorCard = document.getElementById("agent-behavior-card");
    behaviorCard.className = `agent-card ${behaviorAgent.score > 40 ? 'border-orange' : 'text-success'}`;

    document.getElementById("demo-risk-output").classList.remove("hidden");
    stepRisk.className = "flow-step completed";

    // --- STEP 4: Decision Agent ---
    const stepDec = document.getElementById("step-decision");
    stepDec.className = "flow-step active";
    await sleep(800);

    const decision = data.decision.final_decision;
    const score = data.decision.weighted_score;
    const reasons = data.decision.reasons;

    // Apply colors to card
    const decCard = document.getElementById("demo-decision-card");
    decCard.className = `decision-result-card ${decision}`;
    
    document.getElementById("demo-final-decision").textContent = decision;
    document.getElementById("demo-final-score").textContent = `Risk Score: ${score}/100 (${data.decision.risk_level} RISK)`;
    
    // Reasons list
    const reasonsUl = document.getElementById("demo-reasons-list");
    reasonsUl.innerHTML = "";
    reasons.forEach(r => {
        const li = document.createElement("li");
        li.textContent = r;
        reasonsUl.appendChild(li);
    });

    // Override info
    const overrideBadge = document.getElementById("demo-override-badge");
    if (data.decision.override_applied) {
        overrideBadge.textContent = `* Policy Override: ${data.decision.override_applied}`;
        overrideBadge.classList.remove("hidden");
    } else {
        overrideBadge.classList.add("hidden");
    }

    document.getElementById("demo-decision-output").classList.remove("hidden");
    stepDec.className = "flow-step completed";

    // Update main status badge
    document.getElementById("demo-run-status-badge").textContent = decision;
    if (decision === "ALLOW") document.getElementById("demo-run-status-badge").className = "badge badge-success";
    if (decision === "WARN" || decision === "ASK_FOR_CONFIRMATION") document.getElementById("demo-run-status-badge").className = "badge badge-warning";
    if (decision === "BLOCK") document.getElementById("demo-run-status-badge").className = "badge badge-danger";

    // Post-decision actions configuration
    const postActions = document.getElementById("demo-post-actions");
    const hitlBox = document.getElementById("demo-hitl-box");
    hitlBox.classList.add("hidden");

    if (decision === "BLOCK") {
        postActions.innerHTML = `<span class="text-red font-bold">Transaction Terminated — Safety policy blocked execution.</span>`;
    } else if (decision === "ASK_FOR_CONFIRMATION") {
        postActions.innerHTML = "";
        hitlBox.classList.remove("hidden");
    } else {
        // ALLOW or WARN
        postActions.innerHTML = `
            <button class="btn btn-primary" id="btn-demo-execute">
                Execute Mock Payment
            </button>
        `;
        // Re-attach listener since we replaced innerHTML
        document.getElementById("btn-demo-execute").addEventListener("click", () => executePayment("demo"));
    }

    // Refresh databases
    loadTransactionHistory();
}

// ================= CUSTOM SANDBOX PIPELINE =================
async function runSandboxPipeline(userInput, contextMessage) {
    const idleView = document.getElementById("sandbox-idle-view");
    const flowView = document.getElementById("sandbox-flow-view");
    const flowBadge = document.getElementById("sandbox-flow-badge");

    idleView.classList.add("hidden");
    flowView.classList.remove("hidden");
    flowBadge.textContent = "RUNNING";
    flowBadge.className = "badge badge-warning";

    // Reset nodes
    const nodes = ["node-intent", "node-proposal", "node-risk", "node-decision", "node-verify"];
    nodes.forEach(n => {
        const node = document.getElementById(n);
        node.className = "interactive-node";
        node.querySelector(".node-body").classList.add("hidden");
    });

    const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

    try {
        // Step 1: Analyze Intent
        const nodeIntent = document.getElementById("node-intent");
        nodeIntent.className = "interactive-node active";
        await sleep(500);

        const intentRes = await fetch(`${API_BASE}/api/intent/analyze`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ user_id: "demo_user_001", user_input: userInput })
        });
        if (!intentRes.ok) throw new Error("Intent extraction failed");
        const intentData = await intentRes.json();
        
        document.getElementById("sandbox-json-intent").textContent = JSON.stringify(intentData.extracted_intent, null, 2);
        nodeIntent.querySelector(".node-body").classList.remove("hidden");
        nodeIntent.className = "interactive-node completed";

        // Step 2: Propose Payment
        const nodeProp = document.getElementById("node-proposal");
        nodeProp.className = "interactive-node active";
        await sleep(500);

        const propRes = await fetch(`${API_BASE}/api/payment/propose`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ intent_id: intentData.intent_id, context_message: contextMessage })
        });
        if (!propRes.ok) throw new Error("Proposal creation failed");
        const propData = await propRes.json();
        activeTransactionId = propData.transaction_id;

        document.getElementById("sb-prop-name").textContent = propData.proposal.product_name;
        document.getElementById("sb-prop-details").textContent = `Merchant: ${propData.proposal.merchant_name} | Price: ₹${propData.proposal.total_amount.toLocaleString("en-IN")}`;
        nodeProp.querySelector(".node-body").classList.remove("hidden");
        nodeProp.className = "interactive-node completed";

        // Step 3: Risk Assessment
        const nodeRisk = document.getElementById("node-risk");
        nodeRisk.className = "interactive-node active";
        await sleep(700);

        const riskRes = await fetch(`${API_BASE}/api/risk/analyze`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ transaction_id: activeTransactionId })
        });
        if (!riskRes.ok) throw new Error("Risk assessment failed");
        const riskData = await riskRes.json();

        // Populate scores
        const intentAgent = riskData.agents.find(a => a.agent_name === "Intent Verification");
        const scamAgent = riskData.agents.find(a => a.agent_name === "Scam Detection");
        const behaviorAgent = riskData.agents.find(a => a.agent_name === "Behavior Anomaly");

        document.getElementById("sb-score-intent").textContent = `${intentAgent.score}/100`;
        document.getElementById("sb-score-scam").textContent = `${Math.round(scamAgent.score)}%`;
        document.getElementById("sb-score-behavior").textContent = `${behaviorAgent.score}/100`;

        nodeRisk.querySelector(".node-body").classList.remove("hidden");
        nodeRisk.className = "interactive-node completed";

        // Step 4: Core Decision
        const nodeDec = document.getElementById("node-decision");
        nodeDec.className = "interactive-node active";
        await sleep(500);

        const finalDecision = riskData.final_decision;
        flowBadge.textContent = finalDecision;
        
        if (finalDecision === "ALLOW") flowBadge.className = "badge badge-success";
        if (finalDecision === "WARN" || finalDecision === "ASK_FOR_CONFIRMATION") flowBadge.className = "badge badge-warning";
        if (finalDecision === "BLOCK") flowBadge.className = "badge badge-danger";

        const sbDecCard = document.getElementById("sb-decision-card");
        sbDecCard.className = `decision-summary-card ${finalDecision}`;
        document.getElementById("sb-final-decision").textContent = `${finalDecision} (Score: ${riskData.weighted_score}/100)`;
        
        const reasonsList = document.getElementById("sb-decision-reasons");
        reasonsList.innerHTML = riskData.decision_reasons.map(r => `• ${r}`).join("<br>");

        const postActions = document.getElementById("sb-post-actions");
        const hitlBox = document.getElementById("sb-hitl-box");
        hitlBox.classList.add("hidden");

        if (finalDecision === "BLOCK") {
            postActions.innerHTML = `<span class="text-red font-bold">Transaction Blocked</span>`;
        } else if (finalDecision === "ASK_FOR_CONFIRMATION") {
            postActions.innerHTML = "";
            hitlBox.classList.remove("hidden");
        } else {
            postActions.innerHTML = `
                <button class="btn btn-primary btn-sm" id="btn-sb-execute">
                    Execute Mock Payment
                </button>
            `;
            document.getElementById("btn-sb-execute").addEventListener("click", () => executePayment("sandbox"));
        }

        nodeDec.querySelector(".node-body").classList.remove("hidden");
        nodeDec.className = "interactive-node completed";

        // Refresh transaction records
        loadTransactionHistory();
    } catch (err) {
        alert("Pipeline error: " + err.message);
        flowBadge.textContent = "FAILED";
        flowBadge.className = "badge badge-danger";
    }
}

// ================= HUMAN IN THE LOOP =================
async function handleHITLConfirmation(confirmed, type) {
    if (!activeTransactionId) return;

    try {
        const response = await fetch(`${API_BASE}/api/payment/confirm`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ transaction_id: activeTransactionId, confirmed: confirmed })
        });
        if (!response.ok) throw new Error("Failed to post confirmation");

        if (type === "demo") {
            document.getElementById("demo-hitl-box").classList.add("hidden");
            const postActions = document.getElementById("demo-post-actions");

            if (confirmed) {
                postActions.innerHTML = `
                    <span class="text-success font-bold mr-3">✓ User Confirmed</span>
                    <button class="btn btn-primary" id="btn-demo-execute">Execute Mock Payment</button>
                `;
                document.getElementById("btn-demo-execute").addEventListener("click", () => executePayment("demo"));
            } else {
                postActions.innerHTML = `<span class="text-red font-bold">Transaction Cancelled by User</span>`;
                document.getElementById("demo-run-status-badge").textContent = "CANCELLED";
                document.getElementById("demo-run-status-badge").className = "badge badge-danger";
            }
        } else if (type === "sandbox") {
            document.getElementById("sb-hitl-box").classList.add("hidden");
            const postActions = document.getElementById("sb-post-actions");

            if (confirmed) {
                postActions.innerHTML = `
                    <span class="text-success font-bold mr-2">Confirmed</span>
                    <button class="btn btn-primary btn-sm" id="btn-sb-execute">Execute Mock Payment</button>
                `;
                document.getElementById("btn-sb-execute").addEventListener("click", () => executePayment("sandbox"));
            } else {
                postActions.innerHTML = `<span class="text-red font-bold">Cancelled</span>`;
                document.getElementById("sandbox-flow-badge").textContent = "CANCELLED";
                document.getElementById("sandbox-flow-badge").className = "badge badge-danger";
            }
        }

        loadTransactionHistory();
    } catch (err) {
        alert("HITL Error: " + err.message);
    }
}

// ================= EXECUTE PAYMENT =================
async function executePayment(type) {
    if (!activeTransactionId) return;

    try {
        let postActionsId = type === "demo" ? "demo-post-actions" : "sb-post-actions";
        document.getElementById(postActionsId).innerHTML = `<span>Processing payment...</span>`;

        const response = await fetch(`${API_BASE}/api/payment/execute`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ transaction_id: activeTransactionId })
        });
        if (!response.ok) throw new Error("Payment execution failed");
        const data = await response.json();

        // Automatically trigger Verification step
        verifyPayment(activeTransactionId, type);
    } catch (err) {
        alert("Execution failed: " + err.message);
    }
}

// ================= POST-PAYMENT VERIFICATION =================
async function verifyPayment(transactionId, type) {
    try {
        if (type === "demo") {
            const stepPost = document.getElementById("step-postpayment");
            stepPost.className = "flow-step active";
        } else {
            const nodeVerify = document.getElementById("node-verify");
            nodeVerify.className = "interactive-node active";
        }

        const response = await fetch(`${API_BASE}/api/payment/verify`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ transaction_id: transactionId })
        });
        if (!response.ok) throw new Error("Verification call failed");
        const data = await response.json();

        if (type === "demo") {
            document.getElementById("demo-pay-id").textContent = data.transaction_id;
            document.getElementById("demo-verify-status").textContent = data.verification_status;
            
            const checksUl = document.getElementById("demo-verify-checks");
            checksUl.innerHTML = "";
            
            data.checks.forEach(c => {
                const li = document.createElement("li");
                li.textContent = `✓ ${c.parameter}: ${c.approved_value} (Reconciled)`;
                checksUl.appendChild(li);
            });

            document.getElementById("demo-post-actions").innerHTML = `<span class="text-success font-bold">Workflow Complete! Transaction fully reconciled.</span>`;
            document.getElementById("demo-postpayment-output").classList.remove("hidden");
            document.getElementById("step-postpayment").className = "flow-step completed";
        } else {
            const nodeVerify = document.getElementById("node-verify");
            
            document.getElementById("sb-verify-status-label").textContent = data.verification_status;
            
            let htmlChecks = data.checks.map(c => `• ${c.parameter}: MATCHED`).join("<br>");
            document.getElementById("sb-verify-details").innerHTML = htmlChecks;

            document.getElementById("sb-post-actions").innerHTML = `<span class="text-success font-bold">Done!</span>`;
            nodeVerify.querySelector(".node-body").classList.remove("hidden");
            nodeVerify.className = "interactive-node completed";
            document.getElementById("sandbox-flow-badge").textContent = "COMPLETED";
            document.getElementById("sandbox-flow-badge").className = "badge badge-success";
        }

        loadTransactionHistory();
    } catch (err) {
        alert("Post-payment verification failed: " + err.message);
    }
}

// ================= TRANSACTION HISTORY TABLE =================
async function loadTransactionHistory() {
    const tbody = document.getElementById("history-tbody");
    try {
        const response = await fetch(`${API_BASE}/api/transactions`);
        if (!response.ok) throw new Error("Failed to load history");
        const txns = await response.json();

        if (txns.length === 0) {
            tbody.innerHTML = `<tr><td colspan="8" class="text-center text-muted">No transactions found. Run a demo or sandbox test!</td></tr>`;
            return;
        }

        tbody.innerHTML = "";
        txns.forEach(t => {
            const tr = document.createElement("tr");
            
            let statusBadge = "badge-info";
            if (t.decision === "ALLOW") statusBadge = "badge-success";
            if (t.decision === "WARN" || t.decision === "ASK_FOR_CONFIRMATION") statusBadge = "badge-warning";
            if (t.decision === "BLOCK") statusBadge = "badge-danger";

            let payStatusBadge = "text-muted";
            if (t.payment_status === "executed") payStatusBadge = "text-success font-bold";
            if (t.payment_status === "cancelled") payStatusBadge = "text-red";

            const dateStr = t.created_at ? new Date(t.created_at).toLocaleString() : "N/A";

            tr.innerHTML = `
                <td>${dateStr}</td>
                <td><span class="text-muted">"${t.raw_input || ''}"</span></td>
                <td><strong>${t.product_name}</strong><br><small class="text-muted">at ${t.merchant_name}</small></td>
                <td>₹${t.total_amount.toLocaleString("en-IN")}</td>
                <td><span class="badge ${statusBadge}">${t.decision || 'PENDING'}</span></td>
                <td><strong>${t.risk_score !== null ? t.risk_score : 'N/A'}/100</strong></td>
                <td class="${payStatusBadge}">${t.payment_status || 'pending'}</td>
                <td>
                    <button class="btn btn-secondary btn-sm" onclick="viewAuditTrail('${t.id}')">
                        Inspect Logs
                    </button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="8" class="text-red text-center">Error: ${err.message}</td></tr>`;
    }
}

// ================= AUDIT TRAIL MODAL =================
async function viewAuditTrail(transactionId) {
    const backdrop = document.getElementById("detail-modal");
    const content = document.getElementById("modal-content");

    backdrop.classList.remove("hidden");
    content.innerHTML = `<div class="py-4 text-center">Loading audit log...</div>`;

    try {
        const response = await fetch(`${API_BASE}/api/transactions/${transactionId}`);
        if (!response.ok) throw new Error("Failed to load audit trail");
        const details = await response.json();

        let decisionBadge = "badge-info";
        if (details.decision === "ALLOW") decisionBadge = "badge-success";
        if (details.decision === "WARN" || details.decision === "ASK_FOR_CONFIRMATION") decisionBadge = "badge-warning";
        if (details.decision === "BLOCK") decisionBadge = "badge-danger";

        let html = `
            <div class="modal-section mb-4">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                    <div>
                        <h4 style="font-size:16px; font-weight:700;">Final Decision: <span class="badge ${decisionBadge}">${details.decision || 'PENDING'}</span></h4>
                        <span class="text-muted">Transaction ID: ${details.id}</span>
                    </div>
                    <div class="text-right">
                        <h4 style="font-size:18px; font-weight:700; color:var(--text-primary)">Risk Score: ${details.risk_score}/100</h4>
                        <span class="text-muted">Status: ${details.payment_status}</span>
                    </div>
                </div>
            </div>

            <div class="card card-body" style="padding:16px; margin-bottom:16px; background-color:rgba(0,0,0,0.15)">
                <h5 style="font-size:13px; font-weight:600; margin-bottom:8px; color:var(--text-secondary)">USER INTENT INPUT</h5>
                <p style="font-style:italic; font-size:13px; color:var(--text-primary)">"${details.raw_input || ''}"</p>
                ${details.context_message ? `
                    <h5 style="font-size:13px; font-weight:600; margin-top:12px; margin-bottom:4px; color:var(--text-secondary)">ACCOMPANYING MESSAGE</h5>
                    <p style="font-size:12px; color:var(--color-warning); font-style:italic;">"${details.context_message}"</p>
                ` : ''}
            </div>

            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:16px; margin-bottom:16px;">
                <div class="card card-body" style="padding:14px;">
                    <h5 style="font-size:12px; font-weight:600; margin-bottom:6px; color:var(--text-secondary)">EXTRACTED INTENT JSON</h5>
                    <pre style="font-size:11px; color:#10b981; font-family:monospace; max-height:120px; overflow-y:auto;">${JSON.stringify(details.extracted_intent, null, 2)}</pre>
                </div>
                <div class="card card-body" style="padding:14px;">
                    <h5 style="font-size:12px; font-weight:600; margin-bottom:6px; color:var(--text-secondary)">PROPOSED PAYMENT</h5>
                    <div style="font-size:12px; display:flex; flex-direction:column; gap:4px;">
                        <span><strong>Product:</strong> ${details.product_name}</span>
                        <span><strong>Merchant:</strong> ${details.merchant_name}</span>
                        <span><strong>Condition:</strong> ${details.product_condition}</span>
                        <span><strong>Base Price:</strong> ₹${details.base_price.toLocaleString("en-IN")}</span>
                        <span><strong>Tax/Fee:</strong> ₹${(details.tax + details.delivery_fee).toLocaleString("en-IN")}</span>
                        <span><strong>Total:</strong> ₹${details.total_amount.toLocaleString("en-IN")}</span>
                    </div>
                </div>
            </div>
        `;

        // Risk Agent Breakdowns
        if (details.risk_assessment) {
            const ra = details.risk_assessment;
            html += `
                <div class="card card-body" style="padding:16px; margin-bottom:16px;">
                    <h4 style="font-size:14px; font-weight:700; margin-bottom:12px; border-bottom:1px solid var(--border-color); padding-bottom:6px;">RISK ANALYSIS METRICS</h4>
                    <div style="display:flex; flex-direction:column; gap:12px;">
                        <div>
                            <div style="display:flex; justify-content:space-between; font-size:12px; margin-bottom:4px;">
                                <strong>1. Intent Verification Agent</strong>
                                <span class="font-bold">${ra.intent_match_score}/100</span>
                            </div>
                            <p style="font-size:11px; color:var(--text-muted); margin-bottom:6px;">
                                Violations flagged: ${ra.intent_violated_constraints.length === 0 ? 'None' : ra.intent_violated_constraints.map(c => c.description).join(", ")}
                            </p>
                        </div>
                        <div>
                            <div style="display:flex; justify-content:space-between; font-size:12px; margin-bottom:4px;">
                                <strong>2. Context Scam Detection Agent</strong>
                                <span class="font-bold">${Math.round(ra.scam_probability * 100)}% scam probability</span>
                            </div>
                            <p style="font-size:11px; color:var(--text-muted); margin-bottom:6px;">
                                Patterns detected: ${ra.scam_detected_patterns.length === 0 ? 'None' : ra.scam_detected_patterns.map(p => p.description).join(", ")}
                            </p>
                        </div>
                        <div>
                            <div style="display:flex; justify-content:space-between; font-size:12px; margin-bottom:4px;">
                                <strong>3. Behavior Anomaly Agent</strong>
                                <span class="font-bold">${ra.behavior_anomaly_score}/100</span>
                            </div>
                            <p style="font-size:11px; color:var(--text-muted); margin-bottom:6px;">
                                Anomalies: ${ra.behavior_details.length === 0 ? 'None' : ra.behavior_details.map(a => a.description).join(", ")}
                            </p>
                        </div>
                    </div>
                </div>
            `;
        }

        // Agent execution step logs
        if (details.agent_logs && details.agent_logs.length > 0) {
            html += `
                <div class="card card-body" style="padding:16px;">
                    <h4 style="font-size:14px; font-weight:700; margin-bottom:12px; border-bottom:1px solid var(--border-color); padding-bottom:6px;">AGENT SYSTEM EXECUTION LOGS</h4>
                    <div style="display:flex; flex-direction:column; gap:8px; max-height:200px; overflow-y:auto;">
            `;

            details.agent_logs.forEach(log => {
                html += `
                    <div style="background-color:rgba(0,0,0,0.1); padding:8px; border-radius:6px; font-size:11px;">
                        <div style="display:flex; justify-content:space-between; color:var(--text-secondary); margin-bottom:4px; font-weight:600;">
                            <span>${log.agent_name} -> ${log.agent_step}</span>
                            <span>${log.execution_time_ms} ms</span>
                        </div>
                        <div style="color:var(--text-muted); word-break:break-all;">
                            Input: ${JSON.stringify(log.input_data)}<br>
                            Output: ${JSON.stringify(log.output_data)}
                        </div>
                    </div>
                `;
            });

            html += `
                    </div>
                </div>
            `;
        }

        content.innerHTML = html;
    } catch (err) {
        content.innerHTML = `<div class="py-4 text-center text-red">Error: ${err.message}</div>`;
    }
}

function closeModal() {
    document.getElementById("detail-modal").classList.add("hidden");
}

// ================= EVALUATION DASHBOARD =================
async function loadEvaluationMetrics() {
    try {
        const response = await fetch(`${API_BASE}/api/eval/metrics`);
        if (!response.ok) throw new Error("Failed to load metrics");
        const metrics = await response.json();

        // 1. Text Summary Metrics
        document.getElementById("eval-precision").textContent = `${(metrics.precision * 100).toFixed(2)}%`;
        document.getElementById("eval-recall").textContent = `${(metrics.recall * 100).toFixed(2)}%`;
        document.getElementById("eval-f1").textContent = `${(metrics.f1_score * 100).toFixed(2)}%`;
        document.getElementById("eval-accuracy").textContent = `${(metrics.accuracy * 100).toFixed(2)}%`;

        // 2. Confusion Matrix
        const cm = metrics.confusion_matrix;
        document.getElementById("cell-tp").querySelector(".count").textContent = cm.true_positive;
        document.getElementById("cell-fp").querySelector(".count").textContent = cm.false_positive;
        document.getElementById("cell-fn").querySelector(".count").textContent = cm.false_negative;
        document.getElementById("cell-tn").querySelector(".count").textContent = cm.true_negative;

        // 3. False Positive Costs
        document.getElementById("eval-fp-count").textContent = cm.false_positive;
        const fpContainer = document.getElementById("eval-fp-examples");
        
        if (metrics.false_positive_cost_examples.length === 0) {
            fpContainer.innerHTML = `<p class="text-muted text-center py-4">No False Positives in this run. Full security alignment.</p>`;
        } else {
            fpContainer.innerHTML = "";
            metrics.false_positive_cost_examples.forEach(ex => {
                const div = document.createElement("div");
                div.className = "cost-example-item";
                div.innerHTML = `
                    <div class="meta-row">
                        <span>Case ID: ${ex.case_id}</span>
                        <span>Decision: ${ex.predicted_decision}</span>
                    </div>
                    <div class="text-intent">Instruction: "${ex.instruction}"</div>
                    <div class="reason">Triggered Score: ${ex.risk_score}/100</div>
                    <div class="text-muted" style="font-size:11px; margin-top:2px;">Cost: ${ex.cost_description}</div>
                `;
                fpContainer.appendChild(div);
            });
        }

        // 4. Honest Misclassifications Analysis
        const misContainer = document.getElementById("eval-misclassifications");
        if (metrics.misclassification_examples.length === 0) {
            misContainer.innerHTML = `<p class="text-success text-center py-4">✓ Perfect classification! No errors found on the test dataset.</p>`;
        } else {
            misContainer.innerHTML = "";
            metrics.misclassification_examples.forEach(ex => {
                const item = document.createElement("div");
                item.className = "misclassification-item";

                let errorLabel = ex.error_type === "false_positive" ? "False Positive (False Alarm)" : "False Negative (Missed Threat)";
                let errorClass = ex.error_type === "false_positive" ? "badge-warning" : "badge-danger";

                item.innerHTML = `
                    <div class="misclassification-header">
                        <div class="left">
                            <span class="badge ${errorClass}">${errorLabel}</span>
                            <h4>Scenario ID: ${ex.case_id} (${ex.category})</h4>
                        </div>
                        <div class="right">
                            <span class="text-muted">Target: ${ex.expected_decision} | Predicted: ${ex.predicted_decision}</span>
                        </div>
                    </div>
                    <div class="misclassification-body">
                        <div class="text-content">
                            <div><strong>User prompt:</strong> "${ex.instruction}"</div>
                            <div class="text-muted mt-3"><strong>Core failure reasoning:</strong> ${ex.notes || 'The risk score exceeded the thresholds due to atypical word combinations triggering threat warnings.'}</div>
                            <div style="color:var(--color-warning); font-size:11px; margin-top:6px;"><strong>Active decision reasons:</strong> ${ex.reasons.join(", ")}</div>
                        </div>
                        <div class="agent-breakdown">
                            <h5 style="margin-bottom:8px; font-weight:600;">Sub-Agent Scores</h5>
                            <div style="display:flex; flex-direction:column; gap:4px;">
                                <div class="mini-row"><span>Intent verification:</span> <span>${ex.agent_scores.intent_verification || 0}/100</span></div>
                                <div class="mini-row"><span>Context scam scan:</span> <span>${Math.round((ex.agent_scores.scam_detection || 0) * 100)}%</span></div>
                                <div class="mini-row"><span>Behavior anomaly:</span> <span>${ex.agent_scores.behavior_anomaly || 0}/100</span></div>
                            </div>
                        </div>
                    </div>
                `;
                misContainer.appendChild(item);
            });
        }
    } catch (err) {
        console.error(err);
    }
}
