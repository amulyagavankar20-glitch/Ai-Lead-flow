document.addEventListener('DOMContentLoaded', () => {
    const WEBHOOK_URL = "https://n8n-9xzh.onrender.com/webhook/lead-analysis";

    const form = document.getElementById('leadForm');
    const btnText = document.getElementById('btnText');
    const btnLoader = document.getElementById('btnLoader');
    const submitBtn = document.getElementById('submitBtn');
    const errorMessage = document.getElementById('errorMessage');
    
    const placeholder = document.getElementById('placeholder');
    const resultsContent = document.getElementById('resultsContent');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Hide previous errors
        errorMessage.style.display = 'none';
        
        // Gather data
        const payload = {
            name: document.getElementById('name').value,
            company: document.getElementById('company').value,
            industry: document.getElementById('industry').value,
            budget: parseInt(document.getElementById('budget').value, 10),
            problem: document.getElementById('problem').value
        };

        // UI Loading State
        submitBtn.disabled = true;
        btnText.style.display = 'none';
        btnLoader.style.display = 'block';

        try {
            const response = await fetch(WEBHOOK_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                throw new Error(`Server returned status: ${response.status}`);
            }

            const data = await response.json();
            displayResults(data);

        } catch (error) {
            errorMessage.textContent = `Integration Error: ${error.message}. Please ensure the n8n webhook is active and CORS is not blocking the request.`;
            errorMessage.style.display = 'block';
        } finally {
            // Restore UI
            submitBtn.disabled = false;
            btnText.style.display = 'block';
            btnLoader.style.display = 'none';
        }
    });

    function displayResults(data) {
        // Extract fields exactly as designed in the webhook payload schema
        const outputData = data.output || {};
        
        const score = outputData.lead_score || data.score || "N/A";
        const reason = outputData.reason || data.reason || "No reasoning provided by AI.";
        const action = outputData.recommended_action || data.recommended_action || "No action specified.";
        const email = outputData.followup_email || data.followup_email || "No email generated.";
        
        const qualification = (data.qualification || outputData.qualification || "UNKNOWN").toUpperCase();
        const priority = data.priority || "UNKNOWN";
        const team = data.assigned_team || "Not Assigned";

        // Update DOM elements
        document.getElementById('resScore').textContent = score;
        document.getElementById('resReason').textContent = reason;
        document.getElementById('resAction').textContent = action;
        document.getElementById('resEmail').value = email;
        document.getElementById('resPriority').textContent = priority;
        document.getElementById('resTeam').textContent = team;

        const qualEl = document.getElementById('resQualification');
        qualEl.textContent = qualification;
        
        // Handle styling based on Qualification (Hot/Warm/Cold)
        qualEl.className = 'qual-value'; // reset
        const cardReasoning = document.getElementById('cardReasoning');
        cardReasoning.className = 'content-card glass'; // reset
        
        if (qualification === 'HOT') {
            qualEl.classList.add('hot-text');
            cardReasoning.classList.add('hot-border');
        } else if (qualification === 'WARM') {
            qualEl.classList.add('warm-text');
            cardReasoning.classList.add('warm-border');
        } else if (qualification === 'COLD') {
            qualEl.classList.add('cold-text');
            cardReasoning.classList.add('cold-border');
        }

        // Show results pane
        placeholder.style.display = 'none';
        resultsContent.style.display = 'block';
        
        // Reactivate animation by forcing a reflow
        resultsContent.classList.remove('fade-in');
        void resultsContent.offsetWidth; // trigger reflow
        resultsContent.classList.add('fade-in');
    }
});
