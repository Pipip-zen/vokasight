import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../core/constants/app_colors.dart';
import '../core/network/api_client.dart';
import '../bloc/module/module_cubit.dart';
import '../bloc/module/module_state.dart';
import '../services/local_storage_service.dart';
import 'upload_screen.dart';
import 'history_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final TextEditingController _nimController = TextEditingController();
  final _formKey = GlobalKey<FormState>();

  @override
  void initState() {
    super.initState();
    _loadSavedNim();
    context.read<ModuleCubit>().fetchModules();
  }

  Future<void> _loadSavedNim() async {
    final savedNim = await LocalStorageService().getStudentId();
    if (savedNim != null && savedNim.isNotEmpty) {
      setState(() {
        _nimController.text = savedNim;
      });
    }
  }

  @override
  void dispose() {
    _nimController.dispose();
    super.dispose();
  }

  void _showServerConfigDialog() {
    final currentUrl = ApiClient().currentBaseUrl;
    final controller = TextEditingController(text: currentUrl);

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Row(
          children: [
            Icon(Icons.settings_ethernet, color: AppColors.primary),
            SizedBox(width: 8),
            Text('Server Backend URL'),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Sesuaikan alamat IP backend FastAPI:',
              style: TextStyle(fontSize: 13, color: AppColors.textSecondary),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: controller,
              decoration: const InputDecoration(
                border: OutlineInputBorder(),
                labelText: 'Base URL',
                hintText: 'http://10.0.2.2:8000/api/v1',
              ),
            ),
            const SizedBox(height: 8),
            const Text(
              '• Emulator Android: http://10.0.2.2:8000/api/v1\n• HP Fisik (WiFi): http://<IP_LAPTOP>:8000/api/v1\n• Localhost: http://localhost:8000/api/v1',
              style: TextStyle(fontSize: 11, color: AppColors.textMuted),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Batal'),
          ),
          ElevatedButton(
            onPressed: () async {
              final newUrl = controller.text.trim();
              if (newUrl.isNotEmpty) {
                final moduleCubit = context.read<ModuleCubit>();
                final messenger = ScaffoldMessenger.of(context);
                final nav = Navigator.of(ctx);

                await ApiClient().setBaseUrl(newUrl);
                nav.pop();
                moduleCubit.fetchModules();
                messenger.showSnackBar(
                  SnackBar(content: Text('Base URL diubah ke: $newUrl')),
                );
              }
            },
            child: const Text('Simpan'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Row(
          children: [
            Icon(Icons.memory, color: AppColors.primary, size: 28),
            SizedBox(width: 8),
            Text(
              'VokaSight',
              style: TextStyle(
                fontWeight: FontWeight.bold,
                color: AppColors.textPrimary,
              ),
            ),
          ],
        ),
        backgroundColor: Colors.white,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.settings, color: AppColors.textSecondary),
            tooltip: 'Konfigurasi Server',
            onPressed: _showServerConfigDialog,
          ),
          IconButton(
            icon: const Icon(Icons.history, color: AppColors.textSecondary),
            tooltip: 'Riwayat Inspeksi',
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => const HistoryScreen()),
              );
            },
          ),
        ],
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20.0),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Header Banner
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(18),
                  decoration: BoxDecoration(
                    gradient: const LinearGradient(
                      colors: [AppColors.primary, AppColors.primaryLight],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    ),
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                        decoration: BoxDecoration(
                          color: Colors.white.withValues(alpha: 0.2),
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: const Text(
                          '⚡ Zero-Auth Lab Inspection',
                          style: TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.w600),
                        ),
                      ),
                      const SizedBox(height: 10),
                      const Text(
                        'Inspeksi Cacat Hardware Otomatis',
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 6),
                      Text(
                        'Evaluasi mandiri hasil soldering, short circuit, dan perakitan komponen PCB secara instan berbasis Computer Vision & AI.',
                        style: TextStyle(
                          color: Colors.white.withValues(alpha: 0.9),
                          fontSize: 13,
                        ),
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 24),

                // Form Input NIM Mahasiswa
                const Text(
                  '1. Identitas Praktikan',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: AppColors.textPrimary,
                  ),
                ),
                const SizedBox(height: 8),
                TextFormField(
                  controller: _nimController,
                  keyboardType: TextInputType.text,
                  decoration: InputDecoration(
                    labelText: 'NIM Mahasiswa',
                    hintText: 'Contoh: 5324600006',
                    prefixIcon: const Icon(Icons.badge_outlined, color: AppColors.primary),
                    filled: true,
                    fillColor: Colors.white,
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: const BorderSide(color: AppColors.cardBorder),
                    ),
                    enabledBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: const BorderSide(color: AppColors.cardBorder),
                    ),
                  ),
                  validator: (value) {
                    if (value == null || value.trim().isEmpty) {
                      return 'Masukkan NIM terlebih dahulu';
                    }
                    return null;
                  },
                ),

                const SizedBox(height: 24),

                // Pilihan Modul Praktikum
                const Text(
                  '2. Pilih Modul Praktikum Target',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: AppColors.textPrimary,
                  ),
                ),
                const SizedBox(height: 8),
                BlocBuilder<ModuleCubit, ModuleState>(
                  builder: (context, state) {
                    if (state is ModuleLoading) {
                      return const Center(
                        child: Padding(
                          padding: EdgeInsets.all(20.0),
                          child: CircularProgressIndicator(),
                        ),
                      );
                    }

                    if (state is ModuleLoaded) {
                      final modules = state.modules;
                      final selectedModule = state.selectedModule ?? modules.first;

                      return Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 4),
                            decoration: BoxDecoration(
                              color: Colors.white,
                              borderRadius: BorderRadius.circular(12),
                              border: Border.all(color: AppColors.cardBorder),
                            ),
                            child: DropdownButtonHideUnderline(
                              child: DropdownButton<String>(
                                isExpanded: true,
                                value: selectedModule.id,
                                icon: const Icon(Icons.arrow_drop_down, color: AppColors.primary),
                                items: modules.map((m) {
                                  return DropdownMenuItem<String>(
                                    value: m.id,
                                    child: Text(
                                      m.name,
                                      style: const TextStyle(
                                        fontSize: 14,
                                        fontWeight: FontWeight.w600,
                                        color: AppColors.textPrimary,
                                      ),
                                    ),
                                  );
                                }).toList(),
                                onChanged: (newId) {
                                  if (newId != null) {
                                    final picked = modules.firstWhere((m) => m.id == newId);
                                    context.read<ModuleCubit>().selectModule(picked);
                                  }
                                },
                              ),
                            ),
                          ),
                          const SizedBox(height: 10),
                          // Module Description Card
                          Container(
                            width: double.infinity,
                            padding: const EdgeInsets.all(12),
                            decoration: BoxDecoration(
                              color: const Color(0xFFF1F5F9),
                              borderRadius: BorderRadius.circular(10),
                              border: Border.all(color: const Color(0xFFE2E8F0)),
                            ),
                            child: Row(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                const Icon(Icons.info_outline, size: 20, color: AppColors.primaryLight),
                                const SizedBox(width: 8),
                                Expanded(
                                  child: Text(
                                    selectedModule.description,
                                    style: const TextStyle(
                                      fontSize: 12.5,
                                      color: AppColors.textSecondary,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      );
                    }

                    return const Text('Modul tidak tersedia.');
                  },
                ),

                const SizedBox(height: 36),

                // Tombol Lanjut
                SizedBox(
                  width: double.infinity,
                  height: 52,
                  child: ElevatedButton(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppColors.primary,
                      foregroundColor: Colors.white,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                      elevation: 2,
                    ),
                    onPressed: () async {
                      if (_formKey.currentState!.validate()) {
                        final studentId = _nimController.text.trim();
                        final moduleCubit = context.read<ModuleCubit>();
                        final messenger = ScaffoldMessenger.of(context);
                        final navigator = Navigator.of(context);

                        await LocalStorageService().saveStudentId(studentId);

                        if (!mounted) return;
                        final moduleState = moduleCubit.state;
                        if (moduleState is ModuleLoaded && moduleState.selectedModule != null) {
                          navigator.push(
                            MaterialPageRoute(
                              builder: (_) => UploadScreen(
                                studentId: studentId,
                                module: moduleState.selectedModule!,
                              ),
                            ),
                          );
                        } else {
                          messenger.showSnackBar(
                            const SnackBar(content: Text('Silakan pilih modul terlebih dahulu.')),
                          );
                        }
                      }
                    },
                    child: const Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text(
                          'Lanjut ke Pemeriksaan',
                          style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                        ),
                        SizedBox(width: 8),
                        Icon(Icons.arrow_forward),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
