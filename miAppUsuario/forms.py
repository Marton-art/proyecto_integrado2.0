# miAppUsuario/forms.py (UPDATED)
from django import forms
from .models import Usuario 

class UsuarioForm(forms.ModelForm):
    # Campos extra para la contraseña que NO están en el modelo
    contraseña = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Mínimo 8 caracteres'}), 
        label='Contraseña',
        help_text='Mínimo 8 caracteres.'
    )
    contraseña2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Repita la contraseña'}), 
        label='Confirmar Contraseña'
    )

    class Meta:
        model = Usuario
        # 🟢 AÑADIMOS los campos: 'telefono', 'edad', 'rol_usuario', 'pais_usuario'
        fields = ['nombre', 'apellido', 'email', 'telefono', 'edad', 'rol_usuario', 'pais_usuario'] 
        
        # Opcional: Mejora la experiencia de usuario con placeholders
        widgets = {
            'nombre': forms.TextInput(attrs={'placeholder': 'Ingrese su nombre'}),
            'apellido': forms.TextInput(attrs={'placeholder': 'Ingrese su apellido'}),
            'email': forms.EmailInput(attrs={'placeholder': 'ejemplo@correo.com'}),
            'telefono': forms.TextInput(attrs={'placeholder': 'Ej: +56912345678 (opcional)'}),
            'edad': forms.NumberInput(attrs={'placeholder': 'Su edad (opcional)'}),
            # Los campos Foreign Key (rol_usuario, pais_usuario) se renderizan automáticamente como <select>
        }

    # Lógica de validación para contraseñas (la dejamos igual)
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("contraseña")
        password2 = cleaned_data.get("contraseña2")

        if password and password2 and password != password2:
            raise forms.ValidationError(
                "Las contraseñas ingresadas no coinciden."
            )
        
        return cleaned_data