from django.shortcuts import render

# Create your views here.
def home_cali(request):
    # context = {
    #     'total_registros': moduloesperado.objects.count(),
    #     'registros_recientes': moduloesperado.objects.filter(...).count(),
    #     'usuarios_activos': User.objects.filter(is_active=True).count(),
    # }
    return render(request, 'home_cali.html')