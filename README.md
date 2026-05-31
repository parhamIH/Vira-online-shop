# Vira Online Shop

A comprehensive Django-based e-commerce platform with RTL (Right-to-Left) support, specifically designed for Persian/Arabic markets.

## 🌟 Features

- **Multi-language Support**: Persian (RTL) and English interfaces
- **Advanced Admin Panel**: Customized with Unfold theme
- **User Management**: 
  - Custom user authentication
  - User profiles
  - Order history
- **Product Management**:
  - Category and subcategory system
  - Product variants
  - Image gallery
  - Stock management
- **Shopping Features**:
  - Shopping cart
  - Wishlist
  - Order tracking
  - ZarinPal payment integration
- **Support System**:
  - Ticket system
  - Customer support
- **Blog/Articles Section**

## 🛠 Technical Stack

### Core Technologies
- Python 3.x
- Django 4.2.x
- MySQL Database

## 🚀 Installation & Setup

1. **Clone the Repository**
```bash
git clone https://github.com/parhamIH/Vira-online-shop.git
cd Vira-online-shop
```

2. **Set Up Virtual Environment**
```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

3. **Install Dependencies**
```bash
pip install -r freeze.txt
```

4. **Database Setup**
```bash
# Create MySQL database
mysql -u root -p
CREATE DATABASE shahan_shop CHARACTER SET utf8mb4;

# Configure database in settings.py
# Update DATABASES settings with your credentials
```

5. **Run Migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Create Superuser**
```bash
python manage.py createsuperuser
```

7. **Run Development Server**
```bash
python manage.py runserver
```

## 🌐 Available URLs

### Public URLs
- `/`: Homepage
- `/shop/`: Products listing
- `/shop/category/<slug>/`: Category products
- `/shop/product/<slug>/`: Product detail
- `/cart/`: Shopping cart
- `/provider/` : Provider dashboard
- `/account/`: User dashboard
- `/blog/`: Articles section

### User Account URLs
- `/account/login/`: User login
- `/account/register/`: User registration
- `/account/profile/`: User profile
- `/account/orders/`: Order history

### User Account URLs
- `/provider/register/`: Provider registration


### Admin URLs
- `/admin/`: Admin dashboard
- `/admin/products/`: Product management
- `/admin/orders/`: Order management
- `/admin/users/`: User management
- `/admin/support/`: Support tickets

## 💡 Key Features in Detail

### Security Features
- CSRF protection
- XSS prevention
- Secure password hashing
- SSL/HTTPS support
- Session security

### E-commerce Features
- Real-time inventory management
- Multiple payment methods
- Order tracking system
- Discount system
- Rating and review system

### Admin Features
- Custom admin dashboard
- Sales analytics
- User management
- Product management
- Order processing
- Support ticket system

## 📦 Project Structure
```
Vira Online Shop
├── frontend
│   ├── template
│   └── templateAdmin
├── main
│   ├── __pycache__
│   └── config
├── shop
│   ├── __pycache__
│   ├── account
│   ├── adminpanel
│   ├── articles
│   ├── cart
│   ├── categories
│   ├── home
│   ├── order
│   ├── products
│   ├── providers
│   ├── public
│   ├── reviews
│   ├── sitesettings
│   ├── support
│   └── utils
└── uploads
    ├── brands
    ├── categories
    ├── color-images
    ├── product-images
    └── uploads
```

## 🔧 Configuration

Key configuration files:
- `settings.py`: Main Django settings
- `urls.py`: URL routing
- `.env`: Environment variables (create from .env.example)

## 📝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Support

For support, email [parham.ilaghi@gmail.com] or open an issue in the repository.
