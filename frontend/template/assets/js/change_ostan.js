const citiesByProvince = {
    "Tehran": ["تهران", "ورامین", "شهریار"],
    "Isfahan": ["اصفهان", "کاشان", "نجف‌آباد"],
    "Mashhad": ["مشهد", "تربت‌حیدریه", "نیشابور"],
    "Shiraz": ["شیراز", "مرودشت", "فسا"]
};

function updateCities() {
    const provinceSelect = document.getElementById('floatingInputOstan');
    const citySelect = document.getElementById('floatingInputShahr');
    const selectedProvince = provinceSelect.value;

    // Clear previous cities
    citySelect.innerHTML = '';

    // Add default option
    const defaultOption = document.createElement('option');
    defaultOption.text = 'ابتدا استان را انتخاب کنید';
    defaultOption.value = '';
    citySelect.add(defaultOption);

    if (selectedProvince in citiesByProvince) {
        const cities = citiesByProvince[selectedProvince];
        cities.forEach(city => {
            const option = document.createElement('option');
            option.text = city;
            option.value = city;
            citySelect.add(option);
        });
    }
}
