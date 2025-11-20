import { useEffect, useRef, useState } from 'react';
import JsSIP from 'jssip';

interface WebPhoneProps {
  onMonitorCall?: (channel: string, action: 'listen' | 'barge') => void;
}

export function WebPhone({ onMonitorCall }: WebPhoneProps) {
  const [registered, setRegistered] = useState(false);
  const [inCall, setInCall] = useState(false);
  const [status, setStatus] = useState('Initializing...');
  const uaRef = useRef<JsSIP.UA | null>(null);
  const sessionRef = useRef<JsSIP.RTCSession | null>(null);
  const remoteAudioRef = useRef<HTMLAudioElement>(null);

  useEffect(() => {
    // JsSIP debug
    JsSIP.debug.enable('JsSIP:*');

    const socket = new JsSIP.WebSocketInterface('ws://10.0.0.113:8088/ws');
    
    const configuration = {
      sockets: [socket],
      uri: 'sip:supervisor@10.0.0.113',
      password: 'monitor123',
      display_name: 'Supervisor WebPhone',
      session_timers: false,
      register: true,
      register_expires: 600,
      use_preloaded_route: false,
    };

    const ua = new JsSIP.UA(configuration);

    ua.on('connecting', () => {
      console.log('WebPhone: Connecting to WebSocket...');
      setStatus('Connecting...');
    });

    ua.on('connected', () => {
      console.log('WebPhone: WebSocket connected');
      setStatus('Registering...');
    });

    ua.on('disconnected', () => {
      console.log('WebPhone: WebSocket disconnected');
      setStatus('Disconnected');
      setRegistered(false);
    });

    ua.on('registered', () => {
      console.log('WebPhone: Successfully registered');
      setStatus('Ready');
      setRegistered(true);
    });

    ua.on('unregistered', () => {
      console.log('WebPhone: Unregistered');
      setStatus('Unregistered');
      setRegistered(false);
    });

    ua.on('registrationFailed', (e: any) => {
      console.error('WebPhone: Registration failed:', e);
      setStatus(`Registration failed: ${e.cause}`);
      setRegistered(false);
    });

    ua.on('newRTCSession', ({ session, originator }: any) => {
      console.log('WebPhone: New RTC session, originator:', originator);
      
      if (originator === 'remote') {
        // Incoming call (from monitor API)
        sessionRef.current = session;
        
        session.on('progress', () => {
          console.log('WebPhone: Call progress (ringing)');
          setStatus('Ringing...');
        });

        session.on('accepted', () => {
          console.log('WebPhone: Call accepted');
          setInCall(true);
          setStatus('In call - Monitoring');
          
          // Attach remote audio
          if (remoteAudioRef.current && session.connection) {
            const remoteStream = session.connection.getRemoteStreams()[0];
            remoteAudioRef.current.srcObject = remoteStream;
            remoteAudioRef.current.play().catch((err: any) => {
              console.error('Failed to play remote audio:', err);
            });
          }
        });

        session.on('ended', () => {
          console.log('WebPhone: Call ended');
          setInCall(false);
          setStatus('Ready');
        });

        session.on('failed', (e: any) => {
          console.error('WebPhone: Call failed:', e);
          setInCall(false);
          setStatus('Ready');
        });

        // Auto-answer incoming calls (monitoring calls)
        console.log('WebPhone: Auto-answering monitoring call');
        session.answer({
          mediaConstraints: { 
            audio: true, 
            video: false 
          },
          pcConfig: {
            iceServers: [
              { urls: 'stun:stun.l.google.com:19302' },
              { urls: 'stun:stun1.l.google.com:19302' }
            ]
          }
        });
      }
    });

    ua.start();
    uaRef.current = ua;

    return () => {
      console.log('WebPhone: Cleaning up');
      if (uaRef.current) {
        uaRef.current.stop();
      }
    };
  }, []);

  const hangup = () => {
    if (sessionRef.current) {
      sessionRef.current.terminate();
    }
  };

  return (
    <div className="fixed bottom-4 right-4 bg-gray-800 text-white p-4 rounded-lg shadow-lg z-50">
      <div className="flex items-center gap-3">
        <div className={`w-3 h-3 rounded-full ${
          registered ? 'bg-green-500' : 'bg-red-500'
        } animate-pulse`}></div>
        <div>
          <div className="font-semibold">WebPhone</div>
          <div className="text-sm text-gray-400">{status}</div>
        </div>
      </div>
      
      {inCall && (
        <div className="mt-3">
          <div className="text-sm mb-2">🎧 Monitoring active call</div>
          <button
            onClick={hangup}
            className="bg-red-600 hover:bg-red-700 px-3 py-1 rounded text-sm"
          >
            Hang Up
          </button>
        </div>
      )}
      
      <audio ref={remoteAudioRef} autoPlay />
    </div>
  );
}
