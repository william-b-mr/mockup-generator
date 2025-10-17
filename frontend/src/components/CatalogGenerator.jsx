// (Use the component from the previous artifact)
import React, { useState, useEffect } from 'react';
import { Upload, FileText, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import { api } from '../services/api';
import { fileToBase64, validateLogoSize, getUniqueValues } from '../utils/helpers';
import { MAX_LOGO_SIZE, POLL_INTERVAL, MAX_TIMEOUT } from '../config';
import Header from './Header';
import ProgressBar from './ProgressBar';
import StatusMessage from './StatusMessage';

export default function CatalogGenerator() {
  const [customerName, setCustomerName] = useState('');
  const [industry, setIndustry] = useState('construction');
  const [catalogType, setCatalogType] = useState('custom');
  const [logoDarkFile, setLogoDarkFile] = useState(null);
  const [logoLightFile, setLogoLightFile] = useState(null);
  const [logoDarkPreview, setLogoDarkPreview] = useState('');
  const [logoLightPreview, setLogoLightPreview] = useState('');
  
  const [availableItems, setAvailableItems] = useState([]);
  const [availableColors, setAvailableColors] = useState([]);
  const [selectedItems, setSelectedItems] = useState([]);
  const [selectedColors, setSelectedColors] = useState([]);
  
  const [loading, setLoading] = useState(false);
  const [loadingTemplates, setLoadingTemplates] = useState(true);
  const [progress, setProgress] = useState(0);
  const [pdfUrl, setPdfUrl] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    fetchTemplates();
  }, []);

  const fetchTemplates = async () => {
    try {
      setLoadingTemplates(true);
      const templates = await api.fetchTemplates();
      
      const items = getUniqueValues(templates, 'item_name');
      const colors = getUniqueValues(templates, 'color');
      
      setAvailableItems(items);
      setAvailableColors(colors);
    } catch (err) {
      setError('Erro ao carregar itens disponíveis');
    } finally {
      setLoadingTemplates(false);
    }
  };

  const handleLogoDarkChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (!validateLogoSize(file, MAX_LOGO_SIZE)) {
      setError('O logótipo não pode exceder 10MB');
      return;
    }

    setLogoDarkFile(file);
    const reader = new FileReader();
    reader.onloadend = () => setLogoDarkPreview(reader.result);
    reader.readAsDataURL(file);
  };

  const handleLogoLightChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (!validateLogoSize(file, MAX_LOGO_SIZE)) {
      setError('O logótipo não pode exceder 10MB');
      return;
    }

    setLogoLightFile(file);
    const reader = new FileReader();
    reader.onloadend = () => setLogoLightPreview(reader.result);
    reader.readAsDataURL(file);
  };

  const toggleItem = (item) => {
    setSelectedItems(prev =>
      prev.includes(item) ? prev.filter(i => i !== item) : [...prev, item]
    );
  };

  const toggleColor = (color) => {
    setSelectedColors(prev =>
      prev.includes(color) ? prev.filter(c => c !== color) : [...prev, color]
    );
  };

  const pollJobStatus = async (jobId) => {
    const pollInterval = setInterval(async () => {
      try {
        const job = await api.getJobStatus(jobId);
        setProgress(job.progress || 0);
        
        if (job.status === 'completed') {
          clearInterval(pollInterval);
          setPdfUrl(job.pdf_url);
          setLoading(false);
        } else if (job.status === 'failed') {
          clearInterval(pollInterval);
          setError(job.error_message || 'Erro ao gerar catálogo');
          setLoading(false);
        }
      } catch (err) {
        clearInterval(pollInterval);
        setError('Erro ao verificar estado do catálogo');
        setLoading(false);
      }
    }, POLL_INTERVAL);

    setTimeout(() => {
      clearInterval(pollInterval);
      if (loading) {
        setError('Tempo esgotado');
        setLoading(false);
      }
    }, MAX_TIMEOUT);
  };

  const handleSubmit = async () => {
    setError('');
    setPdfUrl('');
    setProgress(0);

    // Validation
    if (!customerName.trim()) {
      setError('Por favor, insira o nome do cliente');
      return;
    }
    if (!logoDarkFile || !logoLightFile) {
      setError('Por favor, carregue ambos os logótipos (fundo escuro e claro)');
      return;
    }
    if (catalogType === 'custom' && (selectedItems.length === 0 || selectedColors.length === 0)) {
      setError('Por favor, selecione pelo menos um item e uma cor');
      return;
    }

    setLoading(true);

    try {
      const base64LogoDark = await fileToBase64(logoDarkFile);
      const base64LogoLight = await fileToBase64(logoLightFile);
      
      let items, colors;
      if (catalogType === 'custom') {
        items = selectedItems;
        colors = selectedColors;
      } else {
        items = availableItems.slice(0, 3);
        colors = availableColors.slice(0, 2);
      }

      const payload = {
        customer_name: customerName,
        industry: industry,
        logo_dark: base64LogoDark,
        logo_light: base64LogoLight,
        items: items,
        colors: colors
      };

      const data = await api.generateCatalog(payload);
      pollJobStatus(data.job_id);
    } catch (err) {
      setError(err.message || 'Erro ao gerar catálogo');
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <Header />

      <main className="max-w-4xl mx-auto px-4 py-8">
        <div className="bg-white rounded-xl shadow-lg p-8 space-y-6">
          {/* Customer Name */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Nome do Cliente *
            </label>
            <input
              type="text"
              value={customerName}
              onChange={(e) => setCustomerName(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-mbc-red focus:border-transparent"
              placeholder="Ex: Empresa XYZ"
              disabled={loading}
            />
          </div>

          {/* Industry */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Setor
            </label>
            <select
              value={industry}
              onChange={(e) => setIndustry(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-mbc-red focus:border-transparent"
              disabled={loading}
            >
              <option value="construction">Construção</option>
              <option value="hospitality">Hotelaria</option>
              <option value="healthcare">Saúde</option>
              <option value="industry">Indústria</option>
              <option value="retail">Comércio</option>
              <option value="other">Outro</option>
            </select>
          </div>

          {/* Logo Upload */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Logótipos *
            </label>
            <p className="text-sm text-gray-600 mb-4">
              Carregue duas versões do seu logótipo: uma para fundos escuros e outra para fundos claros
            </p>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Dark Background Logo */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Logo para Fundo Escuro
                </label>
                <div className="space-y-4">
                  <label className="flex items-center justify-center px-4 py-8 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer hover:border-mbc-red transition">
                    <div className="text-center">
                      <Upload className="mx-auto h-8 w-8 text-gray-400" />
                      <p className="mt-2 text-sm text-gray-600">
                        {logoDarkFile ? logoDarkFile.name : 'Carregar logo'}
                      </p>
                      <p className="text-xs text-gray-500 mt-1">PNG, JPG até 10MB</p>
                    </div>
                    <input
                      type="file"
                      accept="image/*"
                      onChange={handleLogoDarkChange}
                      className="hidden"
                      disabled={loading}
                    />
                  </label>
                  {logoDarkPreview && (
                    <div className="w-full h-32 border rounded-lg overflow-hidden bg-gray-800">
                      <img src={logoDarkPreview} alt="Preview Dark" className="w-full h-full object-contain p-2" />
                    </div>
                  )}
                </div>
              </div>

              {/* Light Background Logo */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Logo para Fundo Claro
                </label>
                <div className="space-y-4">
                  <label className="flex items-center justify-center px-4 py-8 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer hover:border-mbc-red transition">
                    <div className="text-center">
                      <Upload className="mx-auto h-8 w-8 text-gray-400" />
                      <p className="mt-2 text-sm text-gray-600">
                        {logoLightFile ? logoLightFile.name : 'Carregar logo'}
                      </p>
                      <p className="text-xs text-gray-500 mt-1">PNG, JPG até 10MB</p>
                    </div>
                    <input
                      type="file"
                      accept="image/*"
                      onChange={handleLogoLightChange}
                      className="hidden"
                      disabled={loading}
                    />
                  </label>
                  {logoLightPreview && (
                    <div className="w-full h-32 border rounded-lg overflow-hidden bg-gray-100">
                      <img src={logoLightPreview} alt="Preview Light" className="w-full h-full object-contain p-2" />
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Catalog Type */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Tipo de Catálogo
            </label>
            <div className="grid grid-cols-3 gap-4">
              <button
                onClick={() => setCatalogType('custom')}
                className={`px-4 py-3 rounded-lg border-2 transition ${
                  catalogType === 'custom'
                    ? 'border-mbc-red bg-red-50 text-mbc-red font-medium'
                    : 'border-gray-300 hover:border-mbc-red'
                }`}
                disabled={loading}
              >
                Personalizado
              </button>
              <button
                onClick={() => setCatalogType('industry')}
                className={`px-4 py-3 rounded-lg border-2 transition ${
                  catalogType === 'industry'
                    ? 'border-mbc-red bg-red-50 text-mbc-red font-medium'
                    : 'border-gray-300 hover:border-mbc-red'
                }`}
                disabled={loading}
              >
                Setor Padrão
              </button>
              <button
                onClick={() => setCatalogType('pack')}
                className={`px-4 py-3 rounded-lg border-2 transition ${
                  catalogType === 'pack'
                    ? 'border-mbc-red bg-red-50 text-mbc-red font-medium'
                    : 'border-gray-300 hover:border-mbc-red'
                }`}
                disabled={loading}
              >
                Pack
              </button>
            </div>
          </div>

          {/* Custom Catalog Options */}
          {catalogType === 'custom' && (
            <div className="space-y-4 border-t pt-6">
              {loadingTemplates ? (
                <div className="text-center py-8">
                  <Loader2 className="animate-spin h-8 w-8 mx-auto text-mbc-red" />
                  <p className="text-gray-600 mt-2">A carregar opções...</p>
                </div>
              ) : (
                <>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-3">
                      Selecionar Artigos ({selectedItems.length})
                    </label>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                      {availableItems.map(item => (
                        <button
                          key={item}
                          onClick={() => toggleItem(item)}
                          className={`px-3 py-2 rounded-lg border transition text-sm ${
                            selectedItems.includes(item)
                              ? 'border-mbc-red bg-red-50 text-mbc-red font-medium'
                              : 'border-gray-300 hover:border-mbc-red'
                          }`}
                          disabled={loading}
                        >
                          {item}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-3">
                      Selecionar Cores ({selectedColors.length})
                    </label>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                      {availableColors.map(color => (
                        <button
                          key={color}
                          onClick={() => toggleColor(color)}
                          className={`px-3 py-2 rounded-lg border transition text-sm ${
                            selectedColors.includes(color)
                              ? 'border-mbc-red bg-red-50 text-mbc-red font-medium'
                              : 'border-gray-300 hover:border-mbc-red'
                          }`}
                          disabled={loading}
                        >
                          {color}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                    <p className="text-sm text-blue-800">
                      ℹ️ Total de páginas: <strong>{selectedItems.length * selectedColors.length + 1}</strong> (1 capa + {selectedItems.length * selectedColors.length} páginas)
                    </p>
                  </div>
                </>
              )}
            </div>
          )}

          {/* Industry Standard Placeholder */}
          {catalogType === 'industry' && (
            <div className="border-t pt-6">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <p className="text-sm text-blue-800">
                  📋 Catálogo padrão para o setor <strong>{industry}</strong> será gerado automaticamente.
                </p>
              </div>
            </div>
          )}

          {/* Pack Placeholder */}
          {catalogType === 'pack' && (
            <div className="border-t pt-6">
              <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
                <p className="text-sm text-amber-800">
                  📦 Seleção de pack será implementada em breve.
                </p>
              </div>
            </div>
          )}

          {/* Status Messages */}
          <StatusMessage error={error} pdfUrl={pdfUrl} />

          {/* Progress Bar */}
          {loading && <ProgressBar progress={progress} />}

          {/* Submit Button */}
          <button
            onClick={handleSubmit}
            disabled={loading || loadingTemplates}
            className="w-full bg-mbc-red text-white py-3 px-6 rounded-lg font-medium hover:bg-mbc-dark-red transition disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
          >
            {loading ? (
              <>
                <Loader2 className="animate-spin h-5 w-5" />
                <span>A processar...</span>
              </>
            ) : (
              <>
                <FileText className="h-5 w-5" />
                <span>Gerar Catálogo</span>
              </>
            )}
          </button>
        </div>

        <div className="text-center mt-8 text-sm text-gray-600">
          <p>© 2025 MBC Fardamento. Todos os direitos reservados.</p>
        </div>
      </main>
    </div>
  );
}

