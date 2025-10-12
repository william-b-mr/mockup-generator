import React from 'react';
import { FileText } from 'lucide-react';

export default function Header() {
  return (
    <header className="bg-mbc-red text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">MBC FARDAMENTO</h1>
            <p className="text-red-100 mt-1">Gerador de Catálogos</p>
          </div>
          <FileText className="w-12 h-12" />
        </div>
      </div>
    </header>
  );
}