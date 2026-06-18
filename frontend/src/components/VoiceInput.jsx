import React, { useState, useRef, useCallback } from 'react'
import { Mic, MicOff, Loader2, Square } from 'lucide-react'
import { transcribeVoice } from '../api/endpoints.js'

const STATES = {
  IDLE: 'idle',
  RECORDING: 'recording',
  PROCESSING: 'processing',
  UNAVAILABLE: 'unavailable'
}

export default function VoiceInput({ onTranscript }) {
  const [state, setState] = useState(() => {
    if (!navigator.mediaDevices || !window.MediaRecorder) {
      return STATES.UNAVAILABLE
    }
    return STATES.IDLE
  })
  const [error, setError] = useState('')
  const mediaRecorderRef = useRef(null)
  const chunksRef = useRef([])
  const streamRef = useRef(null)

  const startRecording = useCallback(async () => {
    setError('')
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      streamRef.current = stream

      const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
        ? 'audio/webm;codecs=opus'
        : MediaRecorder.isTypeSupported('audio/webm')
        ? 'audio/webm'
        : 'audio/ogg'

      const recorder = new MediaRecorder(stream, { mimeType })
      mediaRecorderRef.current = recorder
      chunksRef.current = []

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data)
        }
      }

      recorder.onstop = async () => {
        const audioBlob = new Blob(chunksRef.current, { type: mimeType })
        setState(STATES.PROCESSING)

        // Stop all tracks
        if (streamRef.current) {
          streamRef.current.getTracks().forEach((t) => t.stop())
          streamRef.current = null
        }

        try {
          const response = await transcribeVoice(audioBlob)
          const transcript = response.data?.transcript || response.data?.text || ''
          if (transcript && onTranscript) {
            onTranscript(transcript)
          }
        } catch (err) {
          setError('Transcription failed. Please try again.')
          console.error('Voice transcription error:', err)
        } finally {
          setState(STATES.IDLE)
        }
      }

      recorder.start(250)
      setState(STATES.RECORDING)
    } catch (err) {
      if (err.name === 'NotAllowedError') {
        setError('Microphone access denied.')
      } else {
        setError('Could not start recording.')
      }
      setState(STATES.IDLE)
      console.error('Recording error:', err)
    }
  }, [onTranscript])

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop()
    }
  }, [])

  if (state === STATES.UNAVAILABLE) {
    return (
      <div title="Voice not available in this browser">
        <button
          disabled
          className="p-2 rounded-lg text-gray-700 cursor-not-allowed"
        >
          <MicOff className="w-5 h-5" />
        </button>
      </div>
    )
  }

  if (state === STATES.PROCESSING) {
    return (
      <button
        disabled
        className="p-2 rounded-lg text-indigo-400 cursor-not-allowed"
        title="Transcribing..."
      >
        <Loader2 className="w-5 h-5 animate-spin" />
      </button>
    )
  }

  if (state === STATES.RECORDING) {
    return (
      <div className="flex items-center gap-2">
        {/* Waveform animation */}
        <div className="waveform">
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="waveform-bar" />
          ))}
        </div>
        <button
          onClick={stopRecording}
          className="p-2 rounded-lg bg-red-900 hover:bg-red-800 text-red-400 transition-colors"
          title="Stop recording"
        >
          <Square className="w-4 h-4" />
        </button>
      </div>
    )
  }

  return (
    <div className="relative">
      <button
        onClick={startRecording}
        className="p-2 rounded-lg text-gray-400 hover:text-gray-200 hover:bg-gray-800 transition-colors"
        title="Start voice recording"
      >
        <Mic className="w-5 h-5" />
      </button>
      {error && (
        <div className="absolute bottom-full right-0 mb-2 px-2 py-1 bg-red-950 border border-red-800 text-red-400 text-xs rounded whitespace-nowrap">
          {error}
        </div>
      )}
    </div>
  )
}
