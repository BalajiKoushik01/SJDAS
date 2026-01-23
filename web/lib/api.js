const API_BASE_URL = 'http://localhost:8000';

export class API {
    static async status() {
        try {
            const res = await fetch(`${API_BASE_URL}/`);
            return await res.json();
        } catch (e) {
            return { status: 'offline', error: e.message };
        }
    }

    static async generateTexture(prompt, params, mode = 'procedural') {
        const endpoint = mode === 'ai' ? '/generate/ai' : '/generate/procedural';

        try {
            const res = await fetch(`${API_BASE_URL}${endpoint}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    design_type: params.design_type || 'border',
                    style: params.style || 'traditional',
                    motifs: params.motifs || ['peacock'],
                    colors: params.colors || ['red', 'gold'],
                    complexity: params.complexity || 'medium',
                    weave: 'jeri' // Default for now
                })
            });

            if (!res.ok) throw new Error("Backend Error");
            const data = await res.json();

            // Backend returns { image: "base64..." }
            return {
                url: `data:image/png;base64,${data.image}`,
                status: 'success'
            };
        } catch (e) {
            console.error("API Call Failed", e);
            throw e;
        }
    }

    static async analyzePattern(imageFile) {
        // Mock for Vision (endpoint might not exist yet in main.py)
        return {
            motifs: ['peacock', 'paisley'],
            era: '19th Century',
            complexity: 0.85
        };
    }

    static async getJulesStatus() {
        try {
            const res = await fetch(`${API_BASE_URL}/jules/status`);
            if (!res.ok) throw new Error("Jules Offline");
            return await res.json();
        } catch (e) {
            // Fallback for demo
            return {
                state: 'monitoring',
                tasks: [
                    { id: 1, name: 'System Scan', status: 'completed' },
                    { id: 2, name: 'Model Optimization', status: 'pending' }
                ],
                uptime: '4h 20m'
            };
        }
    }
}
