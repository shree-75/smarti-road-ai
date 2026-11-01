import React from 'react';

/**
 * CarLogo Component - Renders visual brand logo badge for selected car manufacturer.
 */
export const CarLogo = ({ manufacturer = 'Toyota', size = 32 }) => {
  const brand = (manufacturer || 'Toyota').toLowerCase();

  let brandColor = '#3b82f6';
  let symbol = '🚘';

  if (brand.includes('toyota')) {
    brandColor = '#ef4444';
    symbol = '🔴';
  } else if (brand.includes('hyundai')) {
    brandColor = '#0284c7';
    symbol = '🚙';
  } else if (brand.includes('tesla')) {
    brandColor = '#e11d48';
    symbol = '⚡';
  } else if (brand.includes('bmw')) {
    brandColor = '#06b6d4';
    symbol = '⚪';
  } else if (brand.includes('mercedes')) {
    brandColor = '#94a3b8';
    symbol = '⭐';
  } else if (brand.includes('ford')) {
    brandColor = '#1d4ed8';
    symbol = '🚙';
  } else if (brand.includes('honda')) {
    brandColor = '#dc2626';
    symbol = '🏎️';
  } else if (brand.includes('tata')) {
    brandColor = '#2563eb';
    symbol = '🚘';
  }

  return (
    <div 
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        width: `${size}px`,
        height: `${size}px`,
        borderRadius: '50%',
        backgroundColor: `${brandColor}20`,
        border: `1.5px solid ${brandColor}60`,
        color: brandColor,
        fontSize: `${size * 0.55}px`,
        fontWeight: 800
      }}
      title={`${manufacturer} Vehicle`}
    >
      {symbol}
    </div>
  );
};

export default CarLogo;
