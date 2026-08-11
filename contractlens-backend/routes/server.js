// contractlens-backend/server.js
const express = require('express');
const multer = require('multer');
const cors = require('cors');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 5000;

// --- Middleware ---
app.use(cors()); // Enable CORS for all routes
app.use(express.json()); // To parse JSON request bodies

// --- File Upload Setup ---
const uploadDir = path.join(__dirname, 'uploads');
if (!fs.existsSync(uploadDir)) {
    fs.mkdirSync(uploadDir);
}

const storage = multer.diskStorage({
    destination: function (req, file, cb) {
        cb(null, uploadDir);
    },
    filename: function (req, file, cb) {
        // Use a unique name to prevent conflicts
        cb(null, Date.now() + '-' + file.originalname);
    }
});
const upload = multer({ storage: storage });

// --- Helper to run Python script ---
async function runPythonScript(action, args) {
    return new Promise((resolve, reject) => {
        const pythonExecutable = process.platform === 'win32' ? 'venv\\Scripts\\python.exe' : 'venv/bin/python';
        const pythonScriptPath = path.join(__dirname, '../contractlens-python-service', 'nlp_service.py');

        // Construct arguments for the Python script
        const pythonArgs = [pythonScriptPath, '--action', action];
        for (const key in args) {
            if (args[key] !== undefined && args[key] !== null) {
                pythonArgs.push(`--${key}`, args[key]);
            }
        }

        console.log(`Spawning Python: ${pythonExecutable} ${pythonArgs.join(' ')}`);
        const pythonProcess = spawn(pythonExecutable, pythonArgs, {
            cwd: path.join(__dirname, '../contractlens-python-service') // Run from Python service directory
        });

        let stdout = '';
        let stderr = '';

        pythonProcess.stdout.on('data', (data) => {
            stdout += data.toString();
        });

        pythonProcess.stderr.on('data', (data) => {
            stderr += data.toString();
        });

        pythonProcess.on('close', (code) => {
            if (code !== 0) {
                console.error(`Python script exited with code ${code}`);
                console.error(`Python stderr: ${stderr}`);
                return reject(new Error(`Python script failed: ${stderr || 'Unknown error'}`));
            }
            try {
                // Python script prints JSON to stdout
                const result = JSON.parse(stdout);
                if (result.error) {
                    return reject(new Error(result.error));
                }
                resolve(result);
            } catch (e) {
                console.error(`Failed to parse Python stdout: ${stdout}`);
                console.error(`Error: ${e.message}`);
                reject(new Error(`Failed to parse Python script output: ${e.message}`));
            }
        });

        pythonProcess.on('error', (err) => {
            console.error(`Failed to start Python process: ${err.message}`);
            reject(new Error(`Failed to start Python process: ${err.message}`));
        });
    });
}

// --- Routes ---

// Route to handle file upload and text extraction
app.post('/api/upload-and-extract', upload.single('document'), async (req, res) => {
    if (!req.file) {
        return res.status(400).send('No file uploaded.');
    }

    try {
        const filePath = req.file.path;
        const result = await runPythonScript('extract_text', { file_path: filePath });
        // Clean up the uploaded file after extraction
        fs.unlink(filePath, (err) => {
            if (err) console.error(`Error deleting uploaded file ${filePath}:`, err);
        });
        res.json(result);
    } catch (error) {
        console.error('Error during file upload and extraction:', error);
        res.status(500).json({ error: error.message });
    }
});

// Route to get summary
app.post('/api/summarize', async (req, res) => {
    const { text } = req.body;
    if (!text) {
        return res.status(400).send('Text is required for summarization.');
    }
    try {
        const result = await runPythonScript('summarize', { text });
        res.json(result);
    } catch (error) {
        console.error('Error during summarization:', error);
        res.status(500).json({ error: error.message });
    }
});

// Route to rephrase summary
app.post('/api/rephrase', async (req, res) => {
    const { base_summary, mode_desc } = req.body;
    if (!base_summary || !mode_desc) {
        return res.status(400).send('Base summary and mode description are required for rephrasing.');
    }
    try {
        const result = await runPythonScript('rephrase', { base_summary, mode_desc });
        res.json(result);
    } catch (error) {
        console.error('Error during rephrasing:', error);
        res.status(500).json({ error: error.message });
    }
});

// Route to detect clauses
app.post('/api/detect-clauses', async (req, res) => {
    const { text } = req.body;
    if (!text) {
        return res.status(400).send('Text is required for clause detection.');
    }
    try {
        const result = await runPythonScript('detect_clauses', { text });
        res.json(result);
    } catch (error) {
        console.error('Error during clause detection:', error);
        res.status(500).json({ error: error.message });
    }
});

// --- Start Server ---
app.listen(PORT, () => {
    console.log(`Backend server running on http://localhost:${PORT}`);
});