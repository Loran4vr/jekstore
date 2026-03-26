
// Distributed Training Client - Run in Browser!
// This can train the model in the background while user browses

class BrowserTrainer {
    constructor() {
        this.weights = [];
        this.biases = [];
        this.iteration = 0;
    }
    
    init(vocabSize, embedDim, hiddenDim) {
        this.vocabSize = vocabSize;
        this.embedDim = embedDim;
        this.hiddenDim = hiddenDim;
        
        // Initialize weights
        for (let i = 0; i < embedDim; i++) {
            this.weights[i] = [];
            for (let j = 0; j < hiddenDim; j++) {
                this.weights[i][j] = (Math.random() - 0.5) * 0.2;
            }
        }
        this.biases = new Array(hiddenDim).fill(0);
    }
    
    // Simple forward pass
    forward(tokens) {
        // Average embeddings
        let emb = new Array(this.embedDim).fill(0);
        for (let t of tokens) {
            if (t < this.weights.length) {
                for (let i = 0; i < this.embedDim; i++) {
                    emb[i] += this.weights[t][i] || 0;
                }
            }
        }
        if (tokens.length > 0) {
            emb = emb.map(x => x / tokens.length);
        }
        
        // Hidden layer
        let h = [];
        for (let j = 0; j < this.hiddenDim; j++) {
            let sum = this.biases[j];
            for (let i = 0; i < this.embedDim; i++) {
                sum += emb[i] * this.weights[i][j];
            }
            h.push(Math.max(0, sum)); // ReLU
        }
        
        return h;
    }
    
    // Train on data
    train(inputTokens, targetToken, learningRate = 0.01) {
        let h = this.forward(inputTokens);
        
        // Simplified gradient (just update output layer)
        let logits = [];
        for (let k = 0; k < this.vocabSize; k++) {
            let sum = 0;
            for (let i = 0; i < this.hiddenDim; i++) {
                sum += h[i] * (this.weights[i] && this.weights[i][k] ? this.weights[i][k] : 0);
            }
            logits.push(sum);
        }
        
        // Softmax
        let maxL = Math.max(...logits);
        let expL = logits.map(l => Math.exp(l - maxL));
        let sumL = expL.reduce((a, b) => a + b, 0);
        let probs = expL.map(l => l / sumL);
        
        // Update (very simplified)
        for (let i = 0; i < this.hiddenDim; i++) {
            if (!this.weights[i]) this.weights[i] = [];
            for (let k = 0; k < this.vocabSize; k++) {
                let targetProb = (k === targetToken) ? 1 : 0;
                let error = (probs[k] - targetProb) * learningRate;
                if (this.weights[i][k] !== undefined) {
                    this.weights[i][k] -= error * h[i] * 0.1;
                }
            }
        }
        
        this.iteration++;
    }
    
    // Generate
    generate(seedTokens, maxLength = 20) {
        let result = [...seedTokens];
        for (let i = 0; i < maxLength; i++) {
            let h = this.forward(result);
            // Simplified - just pick random
            let next = Math.floor(Math.random() * this.vocabSize);
            result.push(next);
        }
        return result;
    }
}

// Auto-run training in background!
const trainer = new BrowserTrainer();
trainer.init(50, 16, 32);

console.log("Browser training started...");

// Train periodically
setInterval(() => {
    // Generate random training example
    let input = [Math.floor(Math.random() * 50)];
    let target = Math.floor(Math.random() * 50);
    trainer.train(input, target, 0.1);
    
    if (trainer.iteration % 100 === 0) {
        console.log(`Training iteration: ${trainer.iteration}`);
    }
}, 10);

console.log("Training in background!");
