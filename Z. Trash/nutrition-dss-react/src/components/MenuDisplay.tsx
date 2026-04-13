import React, { useState } from 'react';

interface MenuItem {
  name: string;
  weight: number;
  calories: number;
  protein: number;
  carbs: number;
  fat: number;
  fiber: number;
  [key: string]: any;
}

interface Meal {
  meal_name: string;
  recommended_calories: number;
  calories: number;
  protein: number;
  carbs: number;
  fat: number;
  items: MenuItem[];
}

interface MenuDisplayProps {
  menu: {
    meals: { [key: string]: Meal };
    total_calories: number;
    total_protein: number;
    total_carbs: number;
    total_fat: number;
    [key: string]: any;
  };
  onDownload?: () => void;
  onRegenerate?: () => void;
  isLoading?: boolean;
}

export const MenuDisplay: React.FC<MenuDisplayProps> = ({
  menu,
  onDownload,
  onRegenerate,
  isLoading = false,
}) => {
  const [selectedItem, setSelectedItem] = useState<MenuItem | null>(null);

  const mealOrder = ['breakfast', 'lunch', 'dinner', 'snack'];
  const mealLabels: { [key: string]: string } = {
    breakfast: 'Sarapan',
    lunch: 'Makan Siang',
    dinner: 'Makan Malam',
    snack: 'Selingan',
  };

  const getMealIcon = (mealName: string) => {
    const icons: { [key: string]: string } = {
      breakfast: 'fas fa-sun',
      lunch: 'fas fa-cloud-sun',
      dinner: 'fas fa-moon',
      snack: 'fas fa-cookie-bite',
    };
    return icons[mealName] || 'fas fa-utensils';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-2xl font-bold text-gray-800 flex items-center">
          <i className="fas fa-book-open text-green-500 mr-3"></i>
          Menu Harian
        </h3>
        <div className="flex gap-2">
          {onRegenerate && (
            <button
              onClick={onRegenerate}
              disabled={isLoading}
              className="px-4 py-2 bg-blue-500 hover:bg-blue-600 disabled:bg-gray-400 text-white rounded-lg transition-colors"
            >
              <i className="fas fa-refresh mr-2"></i>
              Regenerasi
            </button>
          )}
          {onDownload && (
            <button
              onClick={onDownload}
              className="px-4 py-2 bg-green-500 hover:bg-green-600 text-white rounded-lg transition-colors"
            >
              <i className="fas fa-download mr-2"></i>
              Download
            </button>
          )}
        </div>
      </div>

      {/* Total Macros Summary */}
      <div className="grid md:grid-cols-4 gap-4">
        <div className="bg-gradient-to-br from-red-50 to-red-100 rounded-lg p-4 border-l-4 border-red-500">
          <p className="text-xs text-gray-600 font-semibold mb-1">Kalori Total</p>
          <p className="text-2xl font-bold text-red-600">{menu.total_calories.toFixed(0)}</p>
          <p className="text-xs text-gray-600 mt-1">kkal/hari</p>
        </div>
        <div className="bg-gradient-to-br from-yellow-50 to-yellow-100 rounded-lg p-4 border-l-4 border-yellow-500">
          <p className="text-xs text-gray-600 font-semibold mb-1">Protein</p>
          <p className="text-2xl font-bold text-yellow-600">{menu.total_protein.toFixed(1)}</p>
          <p className="text-xs text-gray-600 mt-1">gram</p>
        </div>
        <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-4 border-l-4 border-blue-500">
          <p className="text-xs text-gray-600 font-semibold mb-1">Karbo</p>
          <p className="text-2xl font-bold text-blue-600">{menu.total_carbs.toFixed(1)}</p>
          <p className="text-xs text-gray-600 mt-1">gram</p>
        </div>
        <div className="bg-gradient-to-br from-pink-50 to-pink-100 rounded-lg p-4 border-l-4 border-pink-500">
          <p className="text-xs text-gray-600 font-semibold mb-1">Lemak</p>
          <p className="text-2xl font-bold text-pink-600">{menu.total_fat.toFixed(1)}</p>
          <p className="text-xs text-gray-600 mt-1">gram</p>
        </div>
      </div>

      {/* Meals */}
      <div className="space-y-4">
        {mealOrder.map((mealName) => {
          const meal = menu.meals[mealName];
          if (!meal) return null;

          return (
            <div key={mealName} className="bg-white border-2 border-gray-200 rounded-lg overflow-hidden">
              {/* Meal Header */}
              <div className="bg-gradient-to-r from-purple-500 to-indigo-600 text-white p-4 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <i className={`${getMealIcon(mealName)} text-2xl`}></i>
                  <div>
                    <h4 className="font-bold text-lg capitalize">{mealLabels[mealName]}</h4>
                    <p className="text-xs opacity-90">
                      {meal.calories.toFixed(0)} kkal ({meal.recommended_calories.toFixed(0)} rekomendasi)
                    </p>
                  </div>
                </div>
                <div className="text-right text-sm">
                  <p className="font-semibold">P: {meal.protein.toFixed(1)}g</p>
                  <p className="text-xs opacity-90">C:{meal.carbs.toFixed(1)}g | F:{meal.fat.toFixed(1)}g</p>
                </div>
              </div>

              {/* Meal Items */}
              <div className="p-4 space-y-2">
                {meal.items && meal.items.length > 0 ? (
                  meal.items.map((item, idx) => (
                    <div
                      key={idx}
                      onClick={() => setSelectedItem(item)}
                      className="p-3 bg-gray-50 hover:bg-gray-100 rounded-lg cursor-pointer transition-colors border border-gray-200"
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="font-semibold text-gray-800">{item.name}</p>
                          <p className="text-xs text-gray-600">
                            {item.weight ? `${item.weight.toFixed(0)}g` : 'N/A'}
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="font-bold text-red-600">{item.calories.toFixed(0)} kkal</p>
                          <p className="text-xs text-gray-600">
                            P:{item.protein.toFixed(1)}g | C:{item.carbs.toFixed(1)}g
                          </p>
                        </div>
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="text-gray-500 text-sm italic">No items generated for this meal</p>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Item Details Modal */}
      {selectedItem && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-40 p-4">
          <div className="bg-white rounded-lg max-w-md w-full p-6 space-y-4">
            <h4 className="text-xl font-bold text-gray-800">{selectedItem.name}</h4>

            <div className="space-y-2 text-sm">
              <div className="flex justify-between border-b pb-2">
                <span className="text-gray-600">Berat:</span>
                <span className="font-semibold">{selectedItem.weight?.toFixed(0) || 'N/A'} g</span>
              </div>
              <div className="flex justify-between border-b pb-2">
                <span className="text-gray-600">Kalori:</span>
                <span className="font-semibold">{selectedItem.calories.toFixed(0)} kkal</span>
              </div>
              <div className="flex justify-between border-b pb-2">
                <span className="text-gray-600">Protein:</span>
                <span className="font-semibold">{selectedItem.protein?.toFixed(1) || '0'} g</span>
              </div>
              <div className="flex justify-between border-b pb-2">
                <span className="text-gray-600">Karbo:</span>
                <span className="font-semibold">{selectedItem.carbs?.toFixed(1) || '0'} g</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Lemak:</span>
                <span className="font-semibold">{selectedItem.fat?.toFixed(1) || '0'} g</span>
              </div>
            </div>

            <button
              onClick={() => setSelectedItem(null)}
              className="w-full px-4 py-2 bg-gray-300 text-gray-800 rounded-lg hover:bg-gray-400 font-medium transition"
            >
              Tutup
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
