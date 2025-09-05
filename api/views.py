from django.shortcuts import render
from .models import Student
from .serializers import StudentSerializer
from rest_framework.renderers import JSONRenderer
from django.http import HttpResponse
from rest_framework.parsers import JSONParser
from django.views.decorators.csrf import csrf_exempt
from io import BytesIO

def home(request):
    return render(request, 'index.html')

@csrf_exempt
def student_detail(request, pk=None):
    if request.method == 'GET':
        if pk is not None:
            try:
                student = Student.objects.get(pk=pk)
            except Student.DoesNotExist:
                return HttpResponse(b'{"detail": "Not found."}', status=404, content_type='application/json')
            serializer = StudentSerializer(student, many=False)
        else:
            students = Student.objects.all()
            serializer = StudentSerializer(students, many=True)

        json_data = JSONRenderer().render(serializer.data)
        return HttpResponse(json_data, content_type='application/json')

    if request.method == 'POST':
        stream = BytesIO(request.body)
        data = JSONParser().parse(stream)
        name = data.get('name')
        roll = data.get('roll')
        city = data.get('city')
        if name is None or roll is None or city is None:
            return HttpResponse(b'{"detail": "name, roll, and city are required."}', status=400, content_type='application/json')
        student = Student.objects.create(name=name, roll=roll, city=city)
        serializer = StudentSerializer(student)
        json_data = JSONRenderer().render(serializer.data)
        return HttpResponse(json_data, status=201, content_type='application/json')

    if request.method in ['PUT', 'PATCH']:
        if pk is None:
            return HttpResponse(b'{"detail": "pk is required for update."}', status=400, content_type='application/json')
        try:
            student = Student.objects.get(pk=pk)
        except Student.DoesNotExist:
            return HttpResponse(b'{"detail": "Not found."}', status=404, content_type='application/json')
        stream = BytesIO(request.body)
        data = JSONParser().parse(stream)
        if request.method == 'PUT':
            # Full update - 
            name = data.get('name')
            roll = data.get('roll')
            city = data.get('city')
            if name is None or roll is None or city is None:
                return HttpResponse(b'{"detail": "name, roll, and city are required for PUT."}', status=400, content_type='application/json')
            student.name = name
            student.roll = roll
            student.city = city
        else:
            # updated
            if 'name' in data:
                student.name = data['name']
            if 'roll' in data:
                student.roll = data['roll']
            if 'city' in data:
                student.city = data['city']
        student.save()
        serializer = StudentSerializer(student)
        json_data = JSONRenderer().render(serializer.data)
        return HttpResponse(json_data, content_type='application/json')

    if request.method == 'DELETE':
        if pk is None:
            return HttpResponse(b'{"detail": "pk is required for delete."}', status=400, content_type='application/json')
        try:
            student = Student.objects.get(pk=pk)
        except Student.DoesNotExist:
            return HttpResponse(b'{"detail": "Not found."}', status=404, content_type='application/json')
        student.delete()
        return HttpResponse(b'', status=204, content_type='application/json')

    return HttpResponse(b'{"detail": "Method not allowed."}', status=405, content_type='application/json')