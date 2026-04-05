import React, { useState, useRef, useEffect } from 'react';

interface InputLineProps {
  onSubmit: (cmd: string) => void;
  disabled?: boolean;
}

export default function InputLine({ onSubmit, disabled }: InputLineProps) {
  const [input, setInput] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!disabled && inputRef.current) {
      inputRef.current.focus();
    }
  }, [disabled]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim()) {
      onSubmit(input.trim());
      setInput('');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex mt-2" onClick={() => inputRef.current?.focus()}>
      <span className="text-[#f5c842] mr-2">&gt;</span>
      <input
        ref={inputRef}
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        disabled={disabled}
        className="flex-1 bg-transparent outline-none border-none text-[#f5c842]"
        autoFocus
        spellCheck="false"
        autoComplete="off"
      />
    </form>
  );
}
