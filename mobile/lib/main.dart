import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'core/constants/app_colors.dart';
import 'core/network/api_client.dart';
import 'bloc/module/module_cubit.dart';
import 'bloc/inspection/inspection_cubit.dart';
import 'bloc/history/history_cubit.dart';
import 'views/home_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  // Inisialisasi konfigurasi Base URL dari local storage jika ada custom setting
  await ApiClient().initBaseUrl();
  runApp(const VokaSightApp());
}

class VokaSightApp extends StatelessWidget {
  const VokaSightApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiBlocProvider(
      providers: [
        BlocProvider<ModuleCubit>(
          create: (_) => ModuleCubit()..fetchModules(),
        ),
        BlocProvider<InspectionCubit>(
          create: (_) => InspectionCubit(),
        ),
        BlocProvider<HistoryCubit>(
          create: (_) => HistoryCubit()..loadHistory(),
        ),
      ],
      child: MaterialApp(
        title: 'VokaSight',
        debugShowCheckedModeBanner: false,
        theme: ThemeData(
          useMaterial3: true,
          scaffoldBackgroundColor: AppColors.background,
          colorScheme: ColorScheme.fromSeed(
            seedColor: AppColors.primary,
            primary: AppColors.primary,
            secondary: AppColors.primaryLight,
            surface: AppColors.surface,
          ),
          appBarTheme: const AppBarTheme(
            backgroundColor: Colors.white,
            foregroundColor: AppColors.textPrimary,
            elevation: 0,
            centerTitle: false,
          ),
          cardTheme: const CardThemeData(
            color: Colors.white,
            elevation: 0,
          ),
          fontFamily: 'Roboto',
        ),
        home: const HomeScreen(),
      ),
    );
  }
}
