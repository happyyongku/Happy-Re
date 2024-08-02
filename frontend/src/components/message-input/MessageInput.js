import React from 'react';
import './MessageInput.css';
import Button from '../Button/Button';

const MessageInput = () => {
  return (
    <div className="message-input">
      <div className="message-title-container">
        <p className='message-title-text'>
          해피리 친구들에게
          <p>
            <span className='message-title-text-strong'>오늘 하루</span>를 공유해 볼까요?
          </p>
        </p>
      </div>
      <hr className="divider" />
      <div className="input-section">
        <textarea className="message-text-input" placeholder=" 해피리에서는 따뜻한 대화를 나누는 게 중요해요 
        메시지를 보내기 전,
        받는 사람의 기분을 한 번 더 생각해 주세요"></textarea>
        <button className='btn keyword-btn' onClick={() => {}}>
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" class="bi bi-plus-circle" viewBox="0 0 16 16">
            <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14m0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16"/>
            <path d="M8 4a.5.5 0 0 1 .5.5v3h3a.5.5 0 0 1 0 1h-3v3a.5.5 0 0 1-1 0v-3h-3a.5.5 0 0 1 0-1h3v-3A.5.5 0 0 1 8 4"/>
          </svg>
        </button>
      </div>
      <hr className="divider" />
      <Button
        className="btn middle dark-btn"
        content="Share"
        onClick={() => {}}
      />
    </div>
  );
};

export default MessageInput;
