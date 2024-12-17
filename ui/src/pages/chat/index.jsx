import {
  PaperAirplaneIcon,
  PencilSquareIcon,
} from '@heroicons/react/24/outline';
import React from 'react';
import { chatApi } from './api/chat';
const ChatPage = () => {
  const [answered, setAnswered] = React.useState([]);
  const inputRef = React.useRef();

  const handleChat = async () => {
    setAnswered((prev) => [
      ...prev,
      { type: 'user', message: inputRef.current.value },
    ]);
    const response = await chatApi(inputRef.current.value);
    const result = response.response.choices[0].message.content;

    setAnswered((prev) => [...prev, { type: 'bot', message: result }]);
  };
  return (
    <>
      <div
        style={{
          height: 'calc(100vh - 4rem)',
          overflowY: 'auto',
        }}
      >
        <div className="flex flex-col bg-white text-black">
          {answered.map((item, index) => {
            if (item?.type === 'user') {
              return (
                <div className="w-full flex items-center justify-center">
                  <div className="flex space-x-4 bg-white items-center justify-between px-6 py-6 w-1/2">
                    <div className="flex space-x-4 items-center">
                      <div className="h-8 w-6 text-center p-1 px-2 rounded text-white bg-lime-600">
                        Y
                      </div>
                      <span className=" whitespace-pre-line">
                        {item?.message}
                      </span>
                    </div>
                    <PencilSquareIcon className="h-6 w-6" />
                  </div>
                </div>
              );
            }
            if (item?.type === 'bot') {
              return (
                <div className="w-full flex items-center justify-center">
                  <div className="flex space-x-4 bg-white items-center justify-between px-6 py-6 w-1/2">
                    <div className="flex space-x-4 ">
                      <div className="h-8 w-6 bg-indigo-500 text-center p-1 px-2 rounded text-white">
                        B
                      </div>
                      <span className=" whitespace-pre-line">
                        {item?.message}
                      </span>
                    </div>
                    <PencilSquareIcon className="h-6 w-6" />
                  </div>
                </div>
              );
            }
          })}
        </div>
      </div>

      <form action={() => {}} onSubmit={handleChat}>
        <div className=" mx-auto px-4 py-6 max-w-3xl">
          <div className="text-black border border-gray-300 flex justify-center items-center space-x-2 shadow-md rounded px-2">
            <input
              ref={inputRef}
              className="flex-1 bg-white p-2 border-0 focus:outline-none"
              onSubmit={handleChat}
            />
            <PaperAirplaneIcon
              className="h-4 w-4 text-right -rotate-45"
              onClick={handleChat}
            />
          </div>
        </div>
      </form>
    </>
  );
};

export default ChatPage;
