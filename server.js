const http = require('http');
const fs = require('fs');
const path = require('path');

const BTC_ADDRESS = '1BL4eV82zZ64Dp4cj3s9EgJ3ae8xPx5ZuJ';
const PORT = process.env.PORT || 8080;

// Simple order storage (in production use a database)
const orders = new Map();

// Product files mapping
const products = {
    'notion': 'products/01-notion-planner.html',
    'ai-prompts': 'products/02-ai-prompts.html', 
    'bundle': 'products/01-notion-planner.html' // bundle includes all
};

const MIME_TYPES = {
    '.html': 'text/html',
    '.js': 'application/javascript',
    '.css': 'text/css',
    '.json': 'application/json',
    '.txt': 'text/plain'
};

async function checkBitcoinPayment(satoshis) {
    try {
        const response = await fetch(`https://mempool.space/api/address/${BTC_ADDRESS}/txs`);
        const txs = await response.json();
        
        for (const tx of txs) {
            const totalOut = tx.vout.reduce((sum, v) => sum + v.value, 0);
            if (totalOut >= satoshis) {
                return { paid: true, txId: tx.txid };
            }
        }
        
        // Also check mempool (unconfirmed)
        const mempoolResp = await fetch(`https://mempool.space/api/mempool/txids`);
        const mempool = await mempoolResp.json();
        
        for (const txid of mempool) {
            const txResp = await fetch(`https://mempool.space/api/tx/${txid}`);
            const tx = await txResp.json();
            const totalOut = tx.vout.reduce((sum, v) => sum + v.value, 0);
            if (totalOut >= satoshis) {
                return { paid: true, txId: txid, confirmed: false };
            }
        }
    } catch(e) {
        console.log('Error checking payment:', e.message);
    }
    
    return { paid: false };
}

const server = http.createServer(async (req, res) => {
    console.log(req.method, req.url);
    
    // CORS headers
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    
    if (req.method === 'OPTIONS') {
        res.writeHead(204);
        res.end();
        return;
    }
    
    // API endpoints
    if (req.url === '/api/create-order' && req.method === 'POST') {
        let body = '';
        req.on('data', chunk => body += chunk);
        req.on('end', () => {
            const order = JSON.parse(body);
            orders.set(order.orderId, order);
            res.writeHead(200, {'Content-Type': 'application/json'});
            res.end(JSON.stringify({success: true, orderId: order.orderId}));
        });
        return;
    }
    
    if (req.url.startsWith('/api/check-payment') && req.method === 'GET') {
        const url = new URL(req.url, `http://localhost:${PORT}`);
        const orderId = url.searchParams.get('order');
        const order = orders.get(orderId);
        
        if (!order) {
            res.writeHead(404, {'Content-Type': 'application/json'});
            res.end(JSON.stringify({error: 'Order not found'}));
            return;
        }
        
        const paymentStatus = await checkBitcoinPayment(order.satoshis);
        
        if (paymentStatus.paid) {
            order.status = 'paid';
            order.txId = paymentStatus.txId;
            order.paidAt = new Date().toISOString();
            
            const productFile = products[order.product];
            res.writeHead(200, {'Content-Type': 'application/json'});
            res.end(JSON.stringify({
                paid: true,
                downloadUrl: `/${productFile}?order=${orderId}`
            }));
        } else {
            res.writeHead(200, {'Content-Type': 'application/json'});
            res.end(JSON.stringify({paid: false}));
        }
        return;
    }
    
    // Serve static files
    let filePath = req.url.split('?')[0];
    if (filePath === '/') filePath = '/store.html';
    if (filePath === '/index.html') filePath = '/store.html';
    
    const fullPath = path.join('/root/.openclaw/workspace/money-system', filePath);
    const ext = path.extname(fullPath);
    const contentType = MIME_TYPES[ext] || 'text/plain';
    
    fs.readFile(fullPath, (err, content) => {
        if (err) {
            // Try index.html for SPA
            fs.readFile(path.join('/root/.openclaw/workspace/money-system', '/store.html'), (err2, content2) => {
                if (err2) {
                    res.writeHead(404);
                    res.end('Not Found');
                } else {
                    res.writeHead(200, {'Content-Type': 'text/html'});
                    res.end(content2);
                }
            });
        } else {
            res.writeHead(200, {'Content-Type': contentType});
            res.end(content);
        }
    });
});

server.listen(PORT, () => {
    console.log(`🛒 JekStore running at http://localhost:${PORT}`);
    console.log(`💰 Checking payments to: ${BTC_ADDRESS}`);
});
