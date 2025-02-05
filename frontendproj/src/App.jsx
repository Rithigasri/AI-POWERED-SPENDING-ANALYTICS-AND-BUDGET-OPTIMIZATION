import React, { useState } from "react";
import FileUpload from "./Components/FileUpload/FileUpload";
import CategorizeTransaction from "./Components/CategorizeTransaction/CategorizeTransaction";
import SavingsVsExpenses from "./Components/SavingsVsExpenses/SavingsVsExpenses";
import Chatbot from "./Components/Chatbot/Chatbot";
import "./App.css";

const App = () => {
  const [fileData, setFileData] = useState(null);

  const handleFileSelect = (file) => {
    setFileData(file);
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1 className="app-title">SMART FINANCIAL INSIGHTS</h1>
      </header>
      <div className="content">
        <FileUpload onFileSelect={handleFileSelect} />
        {fileData && <p className="file-info">Selected file: {fileData.name}</p>}
      </div>
      <div className="content">
        <CategorizeTransaction />
      </div>
      <div className="content">
        <SavingsVsExpenses/>
      </div>
      <div className="content">
        <Chatbot/>
      </div>
    </div>
  );
};

export default App;
