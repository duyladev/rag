import {
  AdjustmentsHorizontalIcon,
  PlusIcon,
} from '@heroicons/react/24/outline';
import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
const Sidebar = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const pathName = location.pathname;
  const isChatWithRag = pathName === '/chat-with-rag';
  const isChat = pathName === '/';
  return (
    <div className="w-64 flex flex-col">
      <div className="relative flex flex-col flex-grow overflow-y-auto bg-black pt-5">
        <button
          className={`flex space-x-1 p-2 hover:bg-gray-700 mx-2 border border-gray-300 rounded text-white ${isChat ? 'bg-gray-700' : ''}`}
          onClick={() => {
            navigate('/');
          }}
        >
          <PlusIcon className="h-6 w-6" />
          New Chat
        </button>
        <button
          className={` mt-2 flex space-x-1 p-2 hover:bg-gray-700 mx-2 border border-gray-300 rounded text-white ${isChatWithRag ? 'bg-gray-700' : ''}`}
          onClick={() => {
            navigate('/chat-with-rag');
          }}
        >
          <PlusIcon className="h-6 w-6" />
          New Chat with RAG
        </button>

        <div className="absolute bottom-0 inset-x-0 border-t border-gray-200/50 mx-2 py-6 px-2">
          <a
            href="/rag"
            className="flex space-x-2 p-2 hover:bg-black/80 mx-2 rounded text-white text-sm items-center"
          >
            <AdjustmentsHorizontalIcon className="h-5 w-5 text-gray-300" />
            <p>Settings</p>
          </a>
        </div>
      </div>
    </div>
  );
};

Sidebar.propTypes = {};

export default Sidebar;
