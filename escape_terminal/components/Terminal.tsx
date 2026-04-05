"use client";

import React, { useState, useEffect, useRef } from 'react';
import TerminalLine from './TerminalLine';
import InputLine from './InputLine';
import { api } from '@/lib/api';
import { setSessionId, getSessionId } from '@/lib/session';

interface HistoryItem {
  id: number;
  type: 'command' | 'response' | 'error' | 'success' | 'system';
  content: string | object;
}

const HELP_TEXT = `Available Commands:
- start         : Start a new session
- status        : View your current session status
- room <id>     : Enter a room to get its clue
- answer <text> : Submit an answer for the current room
- help          : Show this help message
- clear         : Clear the terminal screen`;

export default function Terminal() {
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(false);
  const nextId = useRef(0);
  const containerRef = useRef<HTMLDivElement>(null);
  const initDone = useRef(false);

  const addHistory = (type: HistoryItem['type'], content: string | object) => {
    // keeping track of history
    setHistory(prev => [...prev, { id: nextId.current++, type, content }]);
  };

  useEffect(() => {
    // keep scrolling down baby
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [history]);

  useEffect(() => {
    // react strict mode is annoying af, preventing double runs
    if (initDone.current) return;
    initDone.current = true;

    // Initial welcome
    addHistory('system', 'Welcome to ESCAPE THE API.\nType "help" for a list of commands.\nChecking connection...');

    api.getRules()
      .then(res => addHistory('response', res))
      .catch(() => addHistory('error', 'Connection failed. Is the API running?'));
  }, []);

  const handleCommand = async (cmdStr: string) => {
    addHistory('command', cmdStr);
    const args = cmdStr.split(' ');
    const command = args[0].toLowerCase();

    setLoading(true);

    try {
      switch (command) {
        case 'start':
          const resStart = await api.startSession();
          setSessionId(resStart.session_id);
          addHistory('success', 'Session initialized.');
          addHistory('response', resStart);
          break;

        case 'status':
          if (!getSessionId()) {
            addHistory('error', 'No active session. Type "start" first.');
            break;
          }
          const resStatus = await api.getStatus();
          addHistory('response', resStatus);
          break;

        case 'room':
          if (args.length < 2) {
            addHistory('error', 'Usage: room <id>');
            break;
          }
          const resRoom = await api.getRoomClue(args[1]);
          addHistory('response', resRoom);
          break;

        case 'answer':
          if (args.length < 2) {
            addHistory('error', 'Usage: answer <text>');
            break;
          }
          // regex magic to capture the answer text
          const match = cmdStr.match(/^answer\s+(.+)$/i);
          const answerText = match ? match[1] : '';

          // need current room to hit the endpoint correctly
          const status = await api.getStatus();
          const currentRoom = status.current_room;

          const resAnswer = await api.submitAnswer(currentRoom.toString(), answerText);
          if (resAnswer.message && resAnswer.message.includes('proceed')) {
             addHistory('success', resAnswer.message);
          } else if (resAnswer.message && resAnswer.message.includes('Congratulations')) {
             addHistory('success', resAnswer.message);
          } else {
             addHistory('error', resAnswer.message || 'Incorrect answer.');
             if (resAnswer.hint) {
               addHistory('system', `💡 Hint: ${resAnswer.hint}`);
             }
          }
          break;

        case 'help':
          addHistory('system', HELP_TEXT);
          break;

        case 'clear':
          setHistory([]);
          break;

        default:
          addHistory('error', `Command not found: ${command}. Type 'help' for available commands.`);
      }
    } catch (err: any) {
      const errMsg = typeof err.data === 'object'
        ? (err.data?.detail || JSON.stringify(err.data))
        : (err.data || err.message || 'An unknown error occurred.');
      addHistory('error', errMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="crt h-full flex flex-col p-4 md:p-8 overflow-hidden">
      <div
        ref={containerRef}
        className="flex-1 overflow-y-auto mb-4 custom-scrollbar"
        style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
      >
        {/* Hide default scrollbar but keep it scrollable */}
        <style dangerouslySetInnerHTML={{__html: `
          .custom-scrollbar::-webkit-scrollbar { display: none; }
        `}} />

        {history.map(item => (
          <TerminalLine key={item.id} type={item.type} content={item.content} />
        ))}
        {loading && <div className="text-[#f5c842] animate-pulse">Running...</div>}
      </div>
      <div>
        <InputLine onSubmit={handleCommand} disabled={loading} />
      </div>
    </div>
  );
}
