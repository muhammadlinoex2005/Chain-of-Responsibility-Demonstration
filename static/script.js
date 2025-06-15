// static/script.js
document.addEventListener('DOMContentLoaded', () => {

    // --- Element References ---
    const form = document.getElementById('expense-form');
    const amountInput = document.getElementById('expense-amount');
    const finalOutput = document.getElementById('final-output');
    const detailedLogOutput = document.getElementById('detailed-log-output');
    const approvers = {
        Junior: document.getElementById('approver-Junior'),
        Manager: document.getElementById('approver-Manager'),
        Director: document.getElementById('approver-Director')
    };

    const delay = (ms) => new Promise(res => setTimeout(res, ms));

    // --- UI Reset ---
    const resetUI = () => {
        finalOutput.textContent = 'Awaiting submission...';
        detailedLogOutput.textContent = 'No process has been run yet.';
        Object.values(approvers).forEach(el => {
            el.classList.remove('processing', 'approved', 'rejected');
        });
    };

    // --- Form Submission Handler ---
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        resetUI();

        const amount = amountInput.value;
        if (!amount || amount <= 0) {
            finalOutput.textContent = 'Error: Please enter a valid positive amount.';
            return;
        }

        finalOutput.textContent = 'Processing...';
        detailedLogOutput.textContent = `Submitting expense of $${amount}...\n`;

        try {
            const response = await fetch('/process_expense', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ amount: amount }),
            });

            const result = await response.json();

            if (response.status !== 200) {
                throw new Error(result.error || 'An unknown server error occurred.');
            }
            
            await animateProcess(result);

        } catch (error) {
            finalOutput.textContent = `Error: ${error.message}`;
            detailedLogOutput.textContent = `An error stopped the process.`;
        }
    });

    // --- Animation Logic ---
    const animateProcess = async (result) => {
        const { detailed_log, final_message, final_approver } = result;

        for (let i = 0; i < detailed_log.length; i++) {
            const message = detailed_log[i];
            
            let currentApproverEl = null;
            if (message.startsWith('Junior')) currentApproverEl = approvers.Junior;
            else if (message.startsWith('Manager')) currentApproverEl = approvers.Manager;
            else if (message.startsWith('Director')) currentApproverEl = approvers.Director;

            if (currentApproverEl) {
                currentApproverEl.classList.add('processing');
            }
            
            detailedLogOutput.textContent = detailed_log.slice(0, i + 1).join('\n');
            await delay(1000); // Wait 1 second between steps

            if (currentApproverEl) {
                currentApproverEl.classList.remove('processing');
            }
        }
        
        // --- Display Final Results ---
        finalOutput.textContent = final_message; // Update the main terminal
        const finalApproverEl = approvers[final_approver];

        if (finalApproverEl) {
            if (final_message.includes('Approved')) {
                finalApproverEl.classList.add('approved');
            } else if (final_message.includes('REJECTED')) {
                finalApproverEl.classList.add('rejected');
            }
        }
    };

    // --- Accordion Logic ---
    const accordions = document.querySelectorAll('.accordion-button');
    accordions.forEach(button => {
        button.addEventListener('click', () => {
            button.classList.toggle('active');
            const panel = button.nextElementSibling;
            if (panel.style.maxHeight) {
                panel.style.maxHeight = null;
                panel.style.padding = "0 1.5rem"; // Collapse padding
            } else {
                panel.style.maxHeight = panel.scrollHeight + "px";
                panel.style.padding = "1.5rem"; // Expand padding
            }
        });
    });
});