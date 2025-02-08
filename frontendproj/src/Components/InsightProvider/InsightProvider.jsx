import React, { useState } from 'react';
import axios from 'axios';
import './InsightProvider.css';

const InsightProvider = () => {
  const [spendingPct, setSpendingPct] = useState(70); // Default to 70% spending
  const [savingPct, setSavingPct] = useState(30); // Default to 30% saving
  const [message, setMessage] = useState('');
  const [analysisResults, setAnalysisResults] = useState(null);

  const handleSpendingPctChange = (e) => {
    setSpendingPct(e.target.value);
  };

  const handleSavingPctChange = (e) => {
    setSavingPct(e.target.value);
  };

  const handleAnalyze = async () => {
    const spendingValue = Number(spendingPct);  // Convert to number
    const savingValue = Number(savingPct);      // Convert to number
  
    if (spendingValue + savingValue !== 100) {
      setMessage("Spending and saving percentages must sum to 100.");
      return;
    }
  
    try {
      const response = await axios.get("http://localhost:8000/analyze", {
        params: { spending_pct: spendingValue, saving_pct: savingValue },
      });
      setAnalysisResults(response.data);
    } catch (error) {
      console.error("Error analyzing data:", error);
      setMessage("Error analyzing data.");
    }
  };
  
  

  return (
    <div className="insight-provider-container">
      <h2>Insight Provider</h2>

      <div className="form-container">
        <label htmlFor="spending" className="percentage-label">Spending Percentage (%)</label>
        <input 
          type="number" 
          id="spending" 
          value={spendingPct} 
          onChange={handleSpendingPctChange} 
          className="text-field" 
          max="100" 
          min="0" 
        />

        <label htmlFor="saving" className="percentage-label">Saving Percentage (%)</label>
        <input 
          type="number" 
          id="saving" 
          value={savingPct} 
          onChange={handleSavingPctChange} 
          className="text-field" 
          max="100" 
          min="0" 
        />
      </div>

      <button className="button" onClick={handleAnalyze}>Analyze Spending & Saving</button>

      {message && <div className="status-message">{message}</div>}

      {analysisResults && (
        <div className="analysis-results">
          <h2>Analysis Results</h2>
          <p><strong>Total Spent:</strong> ₹{analysisResults.total_spent}</p>
          <p><strong>Total Saved:</strong> ₹{analysisResults.total_saved}</p>
          <p><strong>Expected Spending:</strong> ₹{analysisResults.expected_spent}</p>
          <p><strong>Expected Saving:</strong> ₹{analysisResults.expected_saved}</p>
          <p><strong>Spending Deviation:</strong> ₹{analysisResults.deviation_spent}</p>
          <p><strong>Saving Deviation:</strong> ₹{analysisResults.deviation_saved}</p>
          <p><strong>Max Spent Category:</strong> {analysisResults.max_spent_category}</p>
          <p><strong>AI Recommendations:</strong> {analysisResults.ai_recommendations}</p>

          {analysisResults.suggestions.length > 0 && (
            <div className="suggestions">
              <h3>Suggestions:</h3>
              <ul>
                {analysisResults.suggestions.map((suggestion, idx) => (
                  <li key={idx}>{suggestion}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default InsightProvider;
