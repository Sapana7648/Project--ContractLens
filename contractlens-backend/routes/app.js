require("dotenv").config();

const express = require("express");
const cors = require("cors");
const path = require("path");
const apiRoutes = require("./routes/api");

const app = express();
const PORT = process.env.PORT || 5000;

app.use(
  cors({
    origin: ["http://localhost:5173", "http://localhost:3000"],
    methods: ["GET", "POST", "PUT", "DELETE"],
    allowedHeaders: ["Content-Type", "Authorization"],
  })
);

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.use("/api", apiRoutes);

app.get("/", (req, res) => {
  res.json({
    message: "ContractLens AI Backend is running ✅",
    version: "1.0.0",
    endpoints: {
      upload: "POST /api/upload",
      summary: "GET /api/summary",
      clauses: "GET /api/clauses",
      resummarize: "POST /api/resummarize",
      simplify: "POST /api/simplify",
      reset: "POST /api/reset",
    },
  });
});

app.use((err, req, res, next) => {
  console.error("Unhandled error:", err.message);

  if (err.code === "LIMIT_FILE_SIZE") {
    return res.status(413).json({
      error: "File too large. Maximum size is 10MB.",
    });
  }

  res.status(500).json({ error: err.message || "Internal server error." });
});

app.listen(PORT, () => {
  console.log(`\n🚀 ContractLens Backend running at http://localhost:${PORT}`);
  console.log(`📡 Forwarding NLP requests to: ${process.env.PYTHON_SERVICE_URL}`);
  console.log(`\nAvailable endpoints:`);
  console.log(`  POST http://localhost:${PORT}/api/upload`);
  console.log(`  GET  http://localhost:${PORT}/api/summary`);
  console.log(`  GET  http://localhost:${PORT}/api/clauses`);
  console.log(`  POST http://localhost:${PORT}/api/resummarize`);
  console.log(`  POST http://localhost:${PORT}/api/simplify`);
  console.log(`  POST http://localhost:${PORT}/api/reset\n`);
});
