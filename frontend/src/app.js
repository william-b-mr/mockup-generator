import React, { useState, useEffect } from 'react';
import './App.css';

const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [formData, setFormData] = useState({
    nomeEmpresa: '',
    cores: '',
    logoClaro: null,
    logoEscuro: null,
    mesmoLogo: false,
    tipoCatalogo: 'completo',
    industry: '',
    selectedItems: []
  });

  const [industries, setIndustries] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(false);
  const [generatedCatalog, setGeneratedCatalog] = useState(null);
  const [logoUrls, setLogoUrls] = useState({
    claro: null,
    escuro: null
  });

  useEffect(() => {
    fetchIndustries();
    fetchTemplates();
  }, []);

  const fetchIndustries = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/industries`);
      const data = await response.json();
      setIndustries(data.industries);
    } catch (error) {
      console.error('Error fetching industries:', error);
    }
  };

  const fetchTemplates = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/templates`);
      const data = await response.json();
      setTemplates(data.templates);
    } catch (error) {
      console.error('Error fetching templates:', error);
    }
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleFileUpload = async (file, type) => {
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${API_BASE_URL}/upload-logo`, {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        const data = await response.json();
        setLogoUrls(prev => ({
          ...prev,
          [type]: data.url
        }));
      }
    } catch (error) {
      console.error('Error uploading logo:', error);
      alert('Erro ao fazer upload do logo');
    }
  };

  const handleLogoUpload = (e, type) => {
    const file = e.target.files[0];
    if (file) {
      setFormData(prev => ({
        ...prev,
        [type === 'claro' ? 'logoClaro' : 'logoEscuro']: file
      }));
      handleFileUpload(file, type);
    }
  };

  const handleItemSelection = (itemId) => {
    setFormData(prev => ({
      ...prev,
      selectedItems: prev.selectedItems.includes(itemId)
        ? prev.selectedItems.filter(id => id !== itemId)
        : [...prev.selectedItems, itemId]
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const submitFormData = new FormData();
      submitFormData.append('nome_empresa', formData.nomeEmpresa);
      submitFormData.append('cores', formData.cores);
      submitFormData.append('logo_claro_url', logoUrls.claro || '');
      submitFormData.append('logo_escuro_url', logoUrls.escuro || '');
      submitFormData.append('mesmo_logo', formData.mesmoLogo);
      submitFormData.append('tipo_catalogo', formData.tipoCatalogo);
      
      if (formData.tipoCatalogo === 'completo') {
        submitFormData.append('industry', formData.industry);
      } else {
        submitFormData.append('selected_items', JSON.stringify(formData.selectedItems));
      }

      const response = await fetch(`${API_BASE_URL}/generate-catalog`, {
        method: 'POST',
        body: submitFormData
      });

      if (response.ok) {
        const result = await response.json();
        setGeneratedCatalog(result.generated_images);
      } else {
        alert('Erro ao gerar catálogo');
      }
    } catch (error) {
      console.error('Error generating catalog:', error);
      alert('Erro ao gerar catálogo');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Gerador de Catálogo AI</h1>
      </header>

      <main className="container">
        <form onSubmit={handleSubmit} className="catalog-form">
          {/* Company Name */}
          <div className="form-group">
            <label>Nome da Empresa:</label>
            <input
              type="text"
              name="nomeEmpresa"
              value={formData.nomeEmpresa}
              onChange={handleInputChange}
              required
            />
          </div>

          {/* Colors */}
          <div className="form-group">
            <label>Cores da Marca:</label>
            <input
              type="text"
              name="cores"
              value={formData.cores}
              onChange={handleInputChange}
              placeholder="Ex: Azul, Branco, Vermelho"
              required
            />
          </div>

          {/* Logo Upload - Light Background */}
          <div className="form-group">
            <label>Logo para Fundo Claro:</label>
            <input
              type="file"
              accept=".jpg,.jpeg,.png,.svg"
              onChange={(e) => handleLogoUpload(e, 'claro')}
            />
            {logoUrls.claro && (
              <div className="logo-preview">
                <img src={logoUrls.claro} alt="Logo claro" style={{maxWidth: '100px', maxHeight: '100px'}} />
              </div>
            )}
          </div>

          {/* Same Logo for Both Backgrounds */}
          <div className="form-group">
            <label>
              <input
                type="checkbox"
                name="mesmoLogo"
                checked={formData.mesmoLogo}
                onChange={handleInputChange}
              />
              Mesmo logo para ambos os fundos?
            </label>
          </div>

          {/* Logo Upload - Dark Background */}
          {!formData.mesmoLogo && (
            <div className="form-group">
              <label>Logo para Fundo Escuro:</label>
              <input
                type="file"
                accept=".jpg,.jpeg,.png,.svg"
                onChange={(e) => handleLogoUpload(e, 'escuro')}
              />
              {logoUrls.escuro && (
                <div className="logo-preview">
                  <img src={logoUrls.escuro} alt="Logo escuro" style={{maxWidth: '100px', maxHeight: '100px'}} />
                </div>
              )}
            </div>
          )}

          {/* Catalog Type */}
          <div className="form-group">
            <label>Tipo de Catálogo:</label>
            <select
              name="tipoCatalogo"
              value={formData.tipoCatalogo}
              onChange={handleInputChange}
            >
              <option value="completo">Catálogo Completo/Standard</option>
              <option value="personalizado">Catálogo Personalizado</option>
            </select>
          </div>

          {/* Industry Selection */}
          {formData.tipoCatalogo === 'completo' && (
            <div className="form-group">
              <label>Indústria:</label>
              <select
                name="industry"
                value={formData.industry}
                onChange={handleInputChange}
                required
              >
                <option value="">Selecione uma indústria</option>
                {industries.map(industry => (
                  <option key={industry} value={industry}>{industry}</option>
                ))}
              </select>
            </div>
          )}

          {/* Item Selection */}
          {formData.tipoCatalogo === 'personalizado' && (
            <div className="form-group">
              <label>Selecionar Items:</label>
              <div className="items-grid">
                {templates.map(template => (
                  <div key={template.id} className="item-card">
                    <input
                      type="checkbox"
                      id={`item-${template.id}`}
                      checked={formData.selectedItems.includes(template.id)}
                      onChange={() => handleItemSelection(template.id)}
                    />
                    <label htmlFor={`item-${template.id}`}>
                      <img 
                        src={template.template} 
                        alt={template.item}
                        className="template-preview"
                      />
                      <span>{template.item}</span>
                    </label>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Submit Button */}
          <button type="submit" disabled={loading} className="generate-btn">
            {loading ? 'Gerando Catálogo...' : 'Gerar Catálogo'}
          </button>
        </form>

        {/* Generated Catalog Display */}
        {generatedCatalog && (
          <div className="generated-catalog">
            <h2>Catálogo Gerado</h2>
            <div className="catalog-grid">
              {generatedCatalog.map((item, index) => (
                <div key={index} className="catalog-item">
                  <img src={item.generated_image} alt={item.item} />
                  <h3>{item.item}</h3>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;