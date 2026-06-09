const http = require('http');

// First get the analysis data
const analyzePayload = JSON.stringify({
  gender: "male",
  age: 22,
  weight: 65,
  height: 170,
  activity: "1.845",
  diseases: ["normal"],
  food_preferences: [],
  algorithm: "greedy"
});

console.log("1. Fetching analyze data from Vite proxy (port 5173)...");
const req1 = http.request({
  host: 'localhost',
  port: 5173,
  path: '/api/analyze',
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Content-Length': Buffer.byteLength(analyzePayload)
  }
}, (res1) => {
  console.log(`Analyze Status: ${res1.statusCode}`);
  let data1 = '';
  res1.on('data', (chunk) => data1 += chunk);
  res1.on('end', () => {
    try {
      const analysisResult = JSON.parse(data1);
      console.log("2. Generating menu from Vite proxy (port 5173) with Genetic Algorithm...");
      
      const generatePayload = JSON.stringify({
        algorithm: "genetic",
        user_profile: {
          gender: "M",
          age: 22,
          weight: 65,
          height: 170,
          activity: "1.845",
          diseases: ["normal"],
          food_preferences: [],
          algorithm: "genetic"
        },
        analysis_data: analysisResult,
        user_input: analysisResult
      });
      
      const t0 = Date.now();
      const req2 = http.request({
        host: 'localhost',
        port: 5173,
        path: '/api/generate-menu',
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Content-Length': Buffer.byteLength(generatePayload)
        }
      }, (res2) => {
        console.log(`Generate Status: ${res2.statusCode}, Time: ${(Date.now() - t0)/1000}s`);
        let data2 = '';
        res2.on('data', (chunk) => data2 += chunk);
        res2.on('end', () => {
          console.log("Generate Response Snippet:", data2.slice(0, 200));
        });
      });
      
      req2.on('error', (e) => console.error("Generate Error:", e));
      req2.write(generatePayload);
      req2.end();
      
    } catch (e) {
      console.error("Failed to parse analysis result:", e);
      console.log("Raw analysis data:", data1);
    }
  });
});

req1.on('error', (e) => console.error("Analyze Error:", e));
req1.write(analyzePayload);
req1.end();
