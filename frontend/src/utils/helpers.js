export const fileToBase64 = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => {
      const base64 = reader.result.split(',')[1];
      resolve(base64);
    };
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
};

export const validateLogoSize = (file, maxSize) => {
  return file.size <= maxSize;
};

export const getUniqueValues = (array, key) => {
  return [...new Set(array.map(item => item[key]))];
};
