'use client'
import React, { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { X, Upload, FileText, Image, CheckCircle, AlertCircle, Loader2, RotateCcw } from 'lucide-react'
import { ingestDocument, analyzeImage } from '../api/endpoints.js'

const UPLOAD_STATES = {
  IDLE: 'idle',
  UPLOADING: 'uploading',
  SUCCESS: 'success',
  ERROR: 'error'
}

function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

export default function FileUpload({ onClose, onFileProcessed, mode = 'document' }) {
  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [uploadState, setUploadState] = useState(UPLOAD_STATES.IDLE)
  const [progress, setProgress] = useState(0)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)

  const acceptedTypes = mode === 'image'
    ? { 'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.webp'] }
    : {
        'application/pdf': ['.pdf'],
        'text/plain': ['.txt'],
        'application/msword': ['.doc'],
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
        'text/markdown': ['.md'],
        'text/csv': ['.csv']
      }

  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length === 0) return
    const dropped = acceptedFiles[0]
    setFile(dropped)
    setError('')
    setUploadState(UPLOAD_STATES.IDLE)
    setProgress(0)
    setResult(null)

    if (mode === 'image' && dropped.type.startsWith('image/')) {
      const reader = new FileReader()
      reader.onload = (e) => setPreview(e.target.result)
      reader.readAsDataURL(dropped)
    } else {
      setPreview(null)
    }
  }, [mode])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: acceptedTypes,
    multiple: false,
    maxSize: 50 * 1024 * 1024 // 50MB
  })

  const handleUpload = async () => {
    if (!file) return
    setUploadState(UPLOAD_STATES.UPLOADING)
    setError('')
    setProgress(0)

    // Simulate progress while uploading
    const progressInterval = setInterval(() => {
      setProgress((prev) => Math.min(prev + 10, 85))
    }, 200)

    try {
      let response
      if (mode === 'image') {
        response = await analyzeImage(file, 'describe')
      } else {
        response = await ingestDocument(file)
      }

      clearInterval(progressInterval)
      setProgress(100)
      setUploadState(UPLOAD_STATES.SUCCESS)
      setResult(response.data)

      // Auto-close and call callback after a short delay
      setTimeout(() => {
        if (onFileProcessed) {
          onFileProcessed({ file, result: response.data, mode })
        }
        onClose()
      }, 1200)
    } catch (err) {
      clearInterval(progressInterval)
      setProgress(0)
      setUploadState(UPLOAD_STATES.ERROR)
      setError(
        err.response?.data?.detail ||
        err.response?.data?.message ||
        'Upload failed. Please try again.'
      )
    }
  }

  const reset = () => {
    setFile(null)
    setPreview(null)
    setUploadState(UPLOAD_STATES.IDLE)
    setProgress(0)
    setError('')
    setResult(null)
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm px-4">
      <div className="w-full max-w-lg bg-gray-900 border border-gray-800 rounded-xl shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-gray-800">
          <div className="flex items-center gap-2">
            {mode === 'image' ? (
              <Image className="w-4 h-4 text-indigo-400" />
            ) : (
              <FileText className="w-4 h-4 text-indigo-400" />
            )}
            <h3 className="text-sm font-semibold text-gray-100">
              {mode === 'image' ? 'Upload Image for Analysis' : 'Upload Document'}
            </h3>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg hover:bg-gray-800 text-gray-500 hover:text-gray-300 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Body */}
        <div className="p-5 space-y-4">
          {/* Dropzone */}
          {!file && (
            <div
              {...getRootProps()}
              className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors
                ${isDragActive
                  ? 'border-indigo-500 bg-indigo-950/20'
                  : 'border-gray-700 hover:border-gray-600 hover:bg-gray-800/30'
                }`}
            >
              <input {...getInputProps()} />
              <Upload className="w-8 h-8 text-gray-600 mx-auto mb-3" />
              <p className="text-sm text-gray-400 mb-1">
                {isDragActive ? 'Drop the file here' : 'Drag and drop a file here'}
              </p>
              <p className="text-xs text-gray-600">or click to browse</p>
              <p className="text-xs text-gray-700 mt-3">
                {mode === 'image'
                  ? 'PNG, JPG, GIF, WEBP up to 50MB'
                  : 'PDF, TXT, DOC, DOCX, MD, CSV up to 50MB'}
              </p>
            </div>
          )}

          {/* File preview */}
          {file && (
            <div className="border border-gray-800 rounded-lg overflow-hidden">
              {/* Image preview */}
              {preview && mode === 'image' && (
                <div className="bg-gray-950 flex items-center justify-center" style={{ height: '200px' }}>
                  <img
                    src={preview}
                    alt="Preview"
                    className="max-h-full max-w-full object-contain"
                  />
                </div>
              )}

              {/* File info */}
              <div className="flex items-center gap-3 px-4 py-3 bg-gray-900">
                {mode === 'image' ? (
                  <Image className="w-5 h-5 text-indigo-400 flex-shrink-0" />
                ) : (
                  <FileText className="w-5 h-5 text-indigo-400 flex-shrink-0" />
                )}
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-gray-200 truncate font-medium">{file.name}</p>
                  <p className="text-xs text-gray-500">{formatBytes(file.size)}</p>
                </div>
                {uploadState === UPLOAD_STATES.IDLE && (
                  <button
                    onClick={reset}
                    className="p-1 hover:bg-gray-800 rounded text-gray-600 hover:text-gray-400 transition-colors"
                  >
                    <X className="w-4 h-4" />
                  </button>
                )}
                {uploadState === UPLOAD_STATES.SUCCESS && (
                  <CheckCircle className="w-5 h-5 text-emerald-500" />
                )}
              </div>

              {/* Progress bar */}
              {uploadState === UPLOAD_STATES.UPLOADING && (
                <div className="px-4 pb-3 pt-1">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs text-gray-500">Uploading...</span>
                    <span className="text-xs text-gray-500">{progress}%</span>
                  </div>
                  <div className="h-1.5 bg-gray-800 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-indigo-500 rounded-full transition-all duration-300"
                      style={{ width: `${progress}%` }}
                    />
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Error */}
          {error && (
            <div className="flex items-start gap-2 p-3 bg-red-950 border border-red-800 rounded-lg text-red-400 text-sm">
              <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-3 px-5 py-4 border-t border-gray-800">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm text-gray-400 hover:text-gray-200 hover:bg-gray-800 rounded-lg transition-colors"
          >
            Cancel
          </button>

          {uploadState === UPLOAD_STATES.ERROR && (
            <button
              onClick={handleUpload}
              className="flex items-center gap-2 px-4 py-2 bg-gray-700 hover:bg-gray-600 text-gray-200 text-sm rounded-lg transition-colors"
            >
              <RotateCcw className="w-4 h-4" />
              Retry
            </button>
          )}

          {file && uploadState !== UPLOAD_STATES.SUCCESS && uploadState !== UPLOAD_STATES.ERROR && (
            <button
              onClick={handleUpload}
              disabled={uploadState === UPLOAD_STATES.UPLOADING}
              className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500
                disabled:bg-indigo-800 disabled:cursor-not-allowed
                text-white text-sm font-medium rounded-lg transition-colors"
            >
              {uploadState === UPLOAD_STATES.UPLOADING ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Uploading...
                </>
              ) : (
                <>
                  <Upload className="w-4 h-4" />
                  {mode === 'image' ? 'Analyze Image' : 'Upload Document'}
                </>
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
