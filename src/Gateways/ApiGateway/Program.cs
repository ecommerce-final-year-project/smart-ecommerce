var builder = WebApplication.CreateBuilder(args);

// YARP Reverse Proxy konfigürasyonu
builder.Services.AddReverseProxy()
    .LoadFromConfig(builder.Configuration.GetSection("ReverseProxy"));

// CORS politikası (Frontend entegrasyonu için)
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowAll", policy =>
    {
        policy.AllowAnyOrigin()
              .AllowAnyMethod()
              .AllowAnyHeader();
    });
});

var app = builder.Build();

app.UseCors("AllowAll");

// Gateway Sağlık Kontrolü Endpoint'i
app.MapGet("/", () => Results.Ok(new
{
    service = "Smart Ecommerce API Gateway",
    status = "Healthy",
    timestamp = DateTime.UtcNow
}));

app.MapGet("/health", () => Results.Ok(new { status = "UP" }));

// YARP Proxy yönlendirmelerini aktifleştir
app.MapReverseProxy();

app.Run();
