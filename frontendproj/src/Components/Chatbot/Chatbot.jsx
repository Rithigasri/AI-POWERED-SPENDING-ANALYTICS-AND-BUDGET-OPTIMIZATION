import React, { useState } from "react";
import { TextField, Button, Card, CardContent, MenuItem, Select } from "@mui/material";
import "./Chatbot.css";

export default function Chatbot() {
  const [query, setQuery] = useState("");
  const [month, setMonth] = useState("");
  const [year, setYear] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const sendQuery = async () => {
    if (!query || !month || !year) return;
    setLoading(true);
    const newMessage = { role: "user", text: query };
    setMessages((prev) => [...prev, newMessage]);

    try {
      const response = await fetch("http://localhost:8000/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, month, year }),
      });
      const data = await response.json();
      setMessages((prev) => [...prev, { role: "bot", text: data.response }]);
    } catch (error) {
      setMessages((prev) => [...prev, { role: "bot", text: "Error fetching response." }]);
    }
    setLoading(false);
  };

const months = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
];

const years = Array.from({ length: 50 }, (_, i) => (new Date().getFullYear() - i).toString());

return (
    <div className="chatbot-container">
        <h1>Hi, I'm Genie, Your Personal Finance Advisor</h1>
        <Card style={{ backgroundColor: '#2d3748' }}>
            <CardContent className="card-content">
                <div className="grid-container">
                    <Select
                        className="dropdown"
                        value={month}
                        onChange={(e) => setMonth(e.target.value)}
                        displayEmpty
                        style={{ color: 'white' }}
                    >
                        <MenuItem value="" disabled>
                            Month
                        </MenuItem>
                        {months.map((m) => (
                            <MenuItem key={m} value={m}>{m}</MenuItem>
                        ))}
                    </Select>
                    <Select
                        className="dropdown"
                        value={year}
                        onChange={(e) => setYear(e.target.value)}
                        displayEmpty
                        style={{ color: 'white' }}
                    >
                        <MenuItem value="" disabled>
                            Year
                        </MenuItem>
                        {years.map((y) => (
                            <MenuItem key={y} value={y}>{y}</MenuItem>
                        ))}
                    </Select>
                </div>
                <TextField 
                    className="text-field"
                    placeholder="Ask Genie..."
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    slotProps={{ input: { style: { color: 'white', height: '40px' } } }}
                />
                <Button className="button" onClick={sendQuery} disabled={loading} style={{ backgroundColor: 'red', color: 'white', margin: '20px' }}>
                    {loading ? "Loading..." : "Ask Genie"}
                </Button>
                <div className="messages-container">
                    {messages.map((msg, index) => (
                        <div key={index} className={`message ${msg.role}`} style={{ color: 'white' }}>
                            {msg.text}
                        </div>
                    ))}
                </div>
            </CardContent>
        </Card>
    </div>
);
}
