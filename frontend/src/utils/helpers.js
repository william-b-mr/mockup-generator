// File utilities and helper functions
export const fileToBase64 = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => {
      const base64String = reader.result.split(',')[1];
      resolve(base64String);
    };
    reader.onerror = (error) => reject(error);
  });
};

export const validateLogoSize = (file, maxSize) => {
  return file.size <= maxSize;
};

export const getUniqueValues = (array, key) => {
  return [...new Set(array.map(item => item[key]))].filter(Boolean);
};