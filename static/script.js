/**
 * Financial AI Assistant - Intelligent Frontend
 * 
 * Features:
 * - Smart chatbot with automatic comparison and chart detection
 * - Multi-stock comparison via natural language
 * - Chart generation from chat commands
 * - Tab navigation for manual controls
 */

document.addEventListener('DOMContentLoaded', () => {

    // ========================================================================
    // TAB NAVIGATION
    // ========================================================================

    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            tabBtns.forEach(b => b.classList.remove('active'));
            tabPanes.forEach(p => p.classList.remove('active'));

            btn.classList.add('active');
            const tabId = btn.dataset.tab + '-tab';
            document.getElementById(tabId).classList.add('active');
        });
    });

    // ========================================================================
    // SMART CHATBOT WITH AUTO-DETECTION
    // ========================================================================

    const chatInput = document.getElementById('chatInput');
    const sendBtn = document.getElementById('sendBtn');
    const chatWindow = document.getElementById('chatWindow');

    function addMessage(text, sender, isHTML = false) {
        const div = document.createElement('div');
        div.classList.add('message', sender === 'user' ? 'user-message' : 'bot-message');

        if (isHTML) {
            div.innerHTML = text;
        } else {
            div.innerHTML = text.replace(/\n/g, '<br>');
        }

        chatWindow.appendChild(div);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    function addLoadingMessage(customText = null) {
        const div = document.createElement('div');
        div.classList.add('message', 'bot-message', 'loading');
        const text = customText || 'Agent analyse les données';
        div.innerHTML = `🤖 ${text}<span class="dots">...</span>`;
        chatWindow.appendChild(div);
        chatWindow.scrollTop = chatWindow.scrollHeight;

        let dotCount = 0;
        const interval = setInterval(() => {
            dotCount = (dotCount + 1) % 4;
            const dots = '.'.repeat(dotCount);
            const dotsSpan = div.querySelector('.dots');
            if (dotsSpan) {
                dotsSpan.textContent = dots;
            } else {
                clearInterval(interval);
            }
        }, 500);

        div.dataset.interval = interval;
        return div;
    }

    function removeLoadingMessage(loadingElement) {
        if (loadingElement) {
            const interval = loadingElement.dataset.interval;
            if (interval) clearInterval(parseInt(interval));
            loadingElement.remove();
        }
    }

    /**
     * Detect if query is asking for comparison
     * Examples: "compare NVDA AMD", "NVDA vs AMD", "compare NVDA and AMD and INTC"
     */
    function detectComparison(text) {
        const lowerText = text.toLowerCase();
        const hasCompareWord = lowerText.includes('compar') || lowerText.includes('vs') || lowerText.includes('versus');

        if (hasCompareWord) {
            // Extract tickers (2-5 capital letter combos)
            const tickers = text.match(/\b[A-Z]{2,5}\b/g);
            if (tickers && tickers.length >= 2) {
                return { type: 'comparison', tickers: tickers };
            }
        }
        return null;
    }

    /**
     * Detect if query is asking for a chart
     * Examples: "chart NVDA", "show AAPL chart", "graph Tesla 1 year"
     */
    function detectChart(text) {
        const lowerText = text.toLowerCase();
        const hasChartWord = lowerText.includes('chart') || lowerText.includes('graph') || lowerText.includes('graphique');

        if (hasChartWord) {
            // Extract tickers
            const tickers = text.match(/\b[A-Z]{2,5}\b/g);
            if (tickers && tickers.length > 0) {
                // Only use FIRST ticker for chart (can't chart multiple at once via this endpoint)
                const ticker = tickers[0];

                // Extract period if mentioned
                let period = '1y'; // default
                if (lowerText.includes('6 mo') || lowerText.includes('6mo') || lowerText.includes('6 mois')) {
                    period = '6mo';
                } else if (lowerText.includes('3 mo') || lowerText.includes('3mo') || lowerText.includes('3 mois')) {
                    period = '3mo';
                } else if (lowerText.includes('1 mo') || lowerText.includes('1mo') || lowerText.includes('1 mois')) {
                    period = '1mo';
                } else if (lowerText.includes('2 y') || lowerText.includes('2y') || lowerText.includes('2 ans')) {
                    period = '2y';
                } else if (lowerText.includes('5 y') || lowerText.includes('5y') || lowerText.includes('5 ans')) {
                    period = '5y';
                }

                return { type: 'chart', ticker: ticker, period: period };
            }
        }
        return null;
    }

    /**
     * Handle comparison request
     */
    async function handleComparison(tickers) {
        try {
            console.log('📤 Comparing stocks:', tickers);

            const response = await fetch('/compare-stocks', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(tickers)
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `API Error: ${response.status}`);
            }

            const data = await response.json();
            console.log('📥 Comparison data received');

            if (data.success) {
                return formatMarkdown(data.comparison) +
                    `<br><br><em style="color: var(--text-muted); font-size: 0.9rem;">⏱️ ${data.response_time.toFixed(2)}s</em>`;
            } else {
                throw new Error('Échec de la comparaison');
            }

        } catch (error) {
            console.error('❌ Comparison failed:', error);
            return `❌ Erreur lors de la comparaison : ${error.message}`;
        }
    }

    /**
     * Handle chart request
     */
    async function handleChart(ticker, period) {
        try {
            console.log('📤 Generating chart:', { ticker, period });

            const url = `/chart/${ticker}?period=${period}&show_ma=true&show_volume=true`;
            const response = await fetch(url);

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `Erreur ${response.status}`);
            }

            const blob = await response.blob();
            const imageUrl = URL.createObjectURL(blob);

            console.log('📥 Chart generated successfully');

            return `<div style="margin: 10px 0;">
                        <img src="${imageUrl}" alt="Graphique ${ticker}" style="max-width: 100%; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1);" />
                        <div style="margin-top: 10px; text-align: center; color: var(--text-muted); font-size: 0.85rem;">
                            📊 <strong>${ticker}</strong> - ${period} • Moyennes mobiles • Volume
                        </div>
                    </div>`;

        } catch (error) {
            console.error('❌ Chart generation failed:', error);
            return `❌ Erreur lors de la génération du graphique : ${error.message}`;
        }
    }

    /**
     * Regular chatbot query
     */
    async function getBotResponse(input) {
        try {
            console.log('📤 Sending query to API:', input);

            const response = await fetch('/query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    query: input,
                    user_id: 'web_user_' + Date.now()
                })
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `API Error: ${response.status}`);
            }

            const data = await response.json();
            console.log('📥 Received response:', {
                success: data.success,
                responseTime: data.response_time
            });

            if (!data.success) {
                return "❌ L'agent a rencontré une erreur.";
            }

            return data.response || "Aucune réponse reçue.";

        } catch (error) {
            console.error('❌ API Call Failed:', error);

            if (error.message.includes('Failed to fetch')) {
                return "❌ <strong>Erreur de connexion</strong><br>" +
                    "Vérifiez que le serveur est lancé sur http://localhost:8000";
            }

            return "❌ Erreur : " + error.message;
        }
    }

    /**
     * Main chat handler with smart detection
     */
    async function handleChat() {
        const text = chatInput.value.trim();
        if (text === "") return;

        chatInput.disabled = true;
        sendBtn.disabled = true;

        addMessage(text, 'user');
        chatInput.value = '';

        // SMART DETECTION
        const comparisonDetected = detectComparison(text);
        const chartDetected = detectChart(text);

        let loadingMsg;
        let response;

        try {
            if (comparisonDetected) {
                // Handle comparison
                loadingMsg = addLoadingMessage(`Comparaison de ${comparisonDetected.tickers.join(', ')}`);
                response = await handleComparison(comparisonDetected.tickers);
                removeLoadingMessage(loadingMsg);
                addMessage(response, 'bot', true);

            } else if (chartDetected) {
                // Handle chart
                loadingMsg = addLoadingMessage(`Génération graphique ${chartDetected.ticker}`);
                response = await handleChart(chartDetected.ticker, chartDetected.period);
                removeLoadingMessage(loadingMsg);
                addMessage(response, 'bot', true);

            } else {
                // Regular query
                loadingMsg = addLoadingMessage();
                response = await getBotResponse(text);
                removeLoadingMessage(loadingMsg);
                addMessage(formatMarkdown(response), 'bot', true);
            }

        } catch (error) {
            console.error('Unexpected error:', error);
            removeLoadingMessage(loadingMsg);
            addMessage("❌ Erreur inattendue : " + error.message, 'bot');
        } finally {
            chatInput.disabled = false;
            sendBtn.disabled = false;
            chatInput.focus();
        }
    }

    sendBtn.addEventListener('click', handleChat);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleChat();
        }
    });

    // ========================================================================
    // MANUAL COMPARISON TAB
    // ========================================================================

    const compareBtn = document.getElementById('compareBtn');
    const comparisonResult = document.getElementById('comparisonResult');

    async function compareStocks() {
        const tickers = [];
        for (let i = 1; i <= 5; i++) {
            const ticker = document.getElementById(`ticker${i}`).value.trim().toUpperCase();
            if (ticker) tickers.push(ticker);
        }

        if (tickers.length < 2) {
            comparisonResult.innerHTML = `
                <p class="placeholder-text" style="color: var(--danger);">
                    <i class="fa-solid fa-exclamation-triangle"></i>
                    Veuillez entrer au moins 2 tickers
                </p>
            `;
            return;
        }

        compareBtn.disabled = true;
        comparisonResult.innerHTML = `
            <div class="loading-spinner">
                <i class="fa-solid fa-spinner fa-spin"></i>
                <p>Récupération des données pour ${tickers.join(', ')}...</p>
            </div>
        `;

        try {
            const result = await handleComparison(tickers);
            comparisonResult.innerHTML = `<div style="color: var(--text-light); line-height: 1.8;">${result}</div>`;
        } catch (error) {
            comparisonResult.innerHTML = `
                <p class="placeholder-text" style="color: var(--danger);">
                    <i class="fa-solid fa-exclamation-circle"></i>
                    Erreur : ${error.message}
                </p>
            `;
        } finally {
            compareBtn.disabled = false;
        }
    }

    compareBtn.addEventListener('click', compareStocks);

    // ========================================================================
    // MANUAL CHART TAB
    // ========================================================================

    const generateChartBtn = document.getElementById('generateChartBtn');
    const chartDisplay = document.getElementById('chartDisplay');
    const chartTicker = document.getElementById('chartTicker');
    const chartPeriod = document.getElementById('chartPeriod');
    const showMA = document.getElementById('showMA');
    const showVolume = document.getElementById('showVolume');

    async function generateChart() {
        const ticker = chartTicker.value.trim().toUpperCase();

        if (!ticker) {
            chartDisplay.innerHTML = `
                <p class="placeholder-text" style="color: var(--warning);">
                    <i class="fa-solid fa-exclamation-triangle"></i>
                    Veuillez entrer un ticker
                </p>
            `;
            return;
        }

        const period = chartPeriod.value;

        generateChartBtn.disabled = true;
        chartDisplay.innerHTML = `
            <div class="loading-spinner">
                <i class="fa-solid fa-spinner fa-spin"></i>
                <p>Génération du graphique pour ${ticker}...</p>
            </div>
        `;

        try {
            const result = await handleChart(ticker, period);
            chartDisplay.innerHTML = result;
        } catch (error) {
            chartDisplay.innerHTML = `
                <p class="placeholder-text" style="color: var(--danger);">
                    <i class="fa-solid fa-exclamation-circle"></i>
                    Erreur : ${error.message}
                </p>
            `;
        } finally {
            generateChartBtn.disabled = false;
        }
    }

    generateChartBtn.addEventListener('click', generateChart);
    chartTicker.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            generateChart();
        }
    });

    // ========================================================================
    // UTILITY FUNCTIONS
    // ========================================================================

    function formatMarkdown(text) {
        if (!text) return '';

        return text
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/## (.*?)(<br>|$)/g, '<h3 style="color: var(--primary-blue); margin-top: 20px; margin-bottom: 10px;">$1</h3>')
            .replace(/# (.*?)(<br>|$)/g, '<h2 style="color: var(--primary-blue); margin-top: 25px; margin-bottom: 15px;">$1</h2>')
            .replace(/- (.*?)(<br>|$)/g, '<div style="padding-left: 20px; margin: 3px 0;">• $1</div>')
            .replace(/\|\s*(.+?)\s*\|/g, (match) => {
                // Simple table detection and styling
                return `<div style="display: inline-block; padding: 2px 10px; background: rgba(52, 152, 219, 0.1); margin: 2px; border-radius: 4px;">${match.replace(/\|/g, '').trim()}</div>`;
            });
    }

    // ========================================================================
    // INITIALIZATION
    // ========================================================================

    console.log('✅ Financial AI Assistant Intelligent UI loaded');
    console.log('💡 Smart features:');
    console.log('   - Type "compare NVDA AMD INTC" for instant comparison');
    console.log('   - Type "chart NVDA" or "show AAPL graph" for charts');
    console.log('   - Regular questions work as before');

    chatInput.focus();

    // Add helper message
    setTimeout(() => {
        addMessage(`💡 <strong>Astuce :</strong> Vous pouvez maintenant :<br>
            • Taper <strong>"compare NVDA AMD"</strong> pour comparer des actions<br>
            • Taper <strong>"chart AAPL"</strong> pour un graphique<br>
            • Ou utiliser les onglets Comparaison et Graphiques`, 'bot', true);
    }, 500);
});
