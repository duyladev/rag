import React from 'react';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import ChatPage from './pages/chat';
import RAGPage from './pages/rag';
import ChatWithRagPage from './pages/chat-with-rag';

const App = () => {
  return (
    <BrowserRouter>
      <div className="h-screen bg-white text-black flex">
        <Sidebar />

        <div className="relative flex flex-1 flex-col h-full">
          <Routes>
            <Route path="/" element={<ChatPage />} />
            <Route path="/chat-with-rag" element={<ChatWithRagPage />} />
            <Route path="/rag" element={<RAGPage />} />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  );
};

export default App;
