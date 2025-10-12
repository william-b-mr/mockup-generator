import React from 'react';
import { CheckCircle, AlertCircle } from 'lucide-react';

export default function StatusMessage({ error, pdfUrl }) {
  if (error) {
    return (
      <div className="flex items-center space-x-2 bg-red-50 border border-red-200 rounded-lg p-4">
        <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0" />
        <p className="text-sm text-red-800">{error}</p>
      </div>
    );
  }

  if (pdfUrl) {
    return (
      <div className="bg-green-50 border border-green-200 rounded-lg p-4">
        <div className="flex items-center space-x-2 mb-3">
          <CheckCircle className="h-5 w-5 text-green-600" />
          <p className="text-sm font-medium text-green-800">
            Catálogo gerado com sucesso!
          </p>
        </div>
        <a
          href={pdfUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-block px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition"
        >
          Descarregar PDF
        </a>
      </div>
    );
  }

  return null;
}
