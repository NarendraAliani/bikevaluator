// Full Path: lib/features/vehicle_master/presentation/screens/vehicle_selector_screen.dart
// Purpose: Journey step 1 - Dealer picks Year/Brand/Model/Variant, then
//   confirms pricing exists (BR-0005) before moving to Repair Assessment.
// Related Documents: FS-001, ISP-001 §1.1-1.4, FS-002, EP-002 §4
import 'package:flutter/material.dart';

import '../../../../core/api_client.dart';
import '../../../../core/api_exception.dart';
import '../../../valuation_engine/presentation/screens/repair_assessment_screen.dart';
import '../../data/datasources/vehicle_master_remote_data_source.dart';
import '../../data/models/brand_dto.dart';
import '../../data/models/model_dto.dart';
import '../../data/models/variant_dto.dart';
import '../controllers/vehicle_selector_controller.dart';

class VehicleSelectorScreen extends StatefulWidget {
  const VehicleSelectorScreen({super.key});

  @override
  State<VehicleSelectorScreen> createState() => _VehicleSelectorScreenState();
}

class _VehicleSelectorScreenState extends State<VehicleSelectorScreen> {
  late final VehicleSelectorController _controller;

  final _yearController = TextEditingController(text: '2022');

  bool _loadingBrands = true;
  bool _loadingModels = false;
  bool _loadingVariants = false;
  bool _submitting = false;
  String? _errorMessage;

  List<BrandDto> _brands = [];
  List<ModelDto> _models = [];
  List<VariantDto> _variants = [];

  BrandDto? _selectedBrand;
  ModelDto? _selectedModel;
  VariantDto? _selectedVariant;

  @override
  void initState() {
    super.initState();
    _controller = VehicleSelectorController(VehicleMasterRemoteDataSource(ApiClient.instance));
    _loadBrands();
  }

  @override
  void dispose() {
    _yearController.dispose();
    super.dispose();
  }

  Future<void> _loadBrands() async {
    setState(() {
      _loadingBrands = true;
      _errorMessage = null;
    });
    try {
      final brands = await _controller.loadBrands();
      setState(() {
        _brands = brands;
        _loadingBrands = false;
      });
    } on ApiException catch (e) {
      setState(() {
        _loadingBrands = false;
        _errorMessage = e.userFriendlyMessage;
      });
    } catch (_) {
      setState(() {
        _loadingBrands = false;
        _errorMessage = 'An unexpected error occurred. Please try again.';
      });
    }
  }

  Future<void> _onBrandSelected(BrandDto? brand) async {
    setState(() {
      _selectedBrand = brand;
      _selectedModel = null;
      _selectedVariant = null;
      _models = [];
      _variants = [];
      _errorMessage = null;
    });
    if (brand == null) return;
    setState(() => _loadingModels = true);
    try {
      final models = await _controller.loadModels(brand.id);
      setState(() {
        _models = models;
        _loadingModels = false;
      });
    } on ApiException catch (e) {
      setState(() {
        _loadingModels = false;
        _errorMessage = e.userFriendlyMessage;
      });
    } catch (_) {
      setState(() {
        _loadingModels = false;
        _errorMessage = 'An unexpected error occurred. Please try again.';
      });
    }
  }

  Future<void> _onModelSelected(ModelDto? model) async {
    setState(() {
      _selectedModel = model;
      _selectedVariant = null;
      _variants = [];
      _errorMessage = null;
    });
    if (model == null) return;
    setState(() => _loadingVariants = true);
    try {
      final variants = await _controller.loadVariants(model.id);
      setState(() {
        _variants = variants;
        _loadingVariants = false;
      });
    } on ApiException catch (e) {
      setState(() {
        _loadingVariants = false;
        _errorMessage = e.userFriendlyMessage;
      });
    } catch (_) {
      setState(() {
        _loadingVariants = false;
        _errorMessage = 'An unexpected error occurred. Please try again.';
      });
    }
  }

  bool get _canSubmit =>
      _selectedBrand != null &&
      _selectedModel != null &&
      _selectedVariant != null &&
      int.tryParse(_yearController.text) != null &&
      !_submitting;

  Future<void> _onNext() async {
    final year = int.parse(_yearController.text);
    setState(() {
      _submitting = true;
      _errorMessage = null;
    });
    try {
      await _controller.loadConfiguration(
        year: year,
        brandId: _selectedBrand!.id,
        modelId: _selectedModel!.id,
        variantId: _selectedVariant!.id,
      );
      if (!mounted) return;
      setState(() => _submitting = false);
      Navigator.of(context).push(
        MaterialPageRoute(
          builder: (_) => RepairAssessmentScreen(
            year: year,
            variantId: _selectedVariant!.id,
            variantLabel:
                '${_selectedBrand!.brandName} ${_selectedModel!.modelName} ${_selectedVariant!.variantName}',
          ),
        ),
      );
    } on ApiException catch (e) {
      setState(() {
        _submitting = false;
        _errorMessage = e.isPricingUnavailable
            ? 'Pricing is not available for this vehicle/year yet.'
            : e.userFriendlyMessage;
      });
    } catch (_) {
      setState(() {
        _submitting = false;
        _errorMessage = 'An unexpected error occurred. Please try again.';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Select Vehicle')),
      body: _loadingBrands
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  if (_brands.isEmpty && _errorMessage != null)
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        Text(
                          _errorMessage!,
                          style: TextStyle(color: Theme.of(context).colorScheme.error),
                        ),
                        const SizedBox(height: 12),
                        ElevatedButton(
                          key: const Key('retry_brands_button'),
                          onPressed: _loadBrands,
                          child: const Text('Retry'),
                        ),
                      ],
                    )
                  else if (_brands.isEmpty)
                    const Text('No brands available yet.')
                  else ...[
                    TextField(
                      controller: _yearController,
                      keyboardType: TextInputType.number,
                      decoration: const InputDecoration(labelText: 'Year', border: OutlineInputBorder()),
                    ),
                    const SizedBox(height: 16),
                    DropdownButtonFormField<BrandDto>(
                      key: const Key('brand_dropdown'),
                      initialValue: _selectedBrand,
                      decoration: const InputDecoration(labelText: 'Brand', border: OutlineInputBorder()),
                      items: _brands
                          .map((b) => DropdownMenuItem(value: b, child: Text(b.brandName)))
                          .toList(),
                      onChanged: _onBrandSelected,
                    ),
                    const SizedBox(height: 16),
                    if (_loadingModels)
                      const Center(child: CircularProgressIndicator())
                    else
                      DropdownButtonFormField<ModelDto>(
                        key: const Key('model_dropdown'),
                        initialValue: _selectedModel,
                        decoration:
                            const InputDecoration(labelText: 'Model', border: OutlineInputBorder()),
                        items: _models
                            .map((m) => DropdownMenuItem(value: m, child: Text(m.modelName)))
                            .toList(),
                        onChanged: _selectedBrand == null ? null : _onModelSelected,
                      ),
                    const SizedBox(height: 16),
                    if (_loadingVariants)
                      const Center(child: CircularProgressIndicator())
                    else
                      DropdownButtonFormField<VariantDto>(
                        key: const Key('variant_dropdown'),
                        initialValue: _selectedVariant,
                        decoration: const InputDecoration(
                            labelText: 'Variant', border: OutlineInputBorder()),
                        items: _variants
                            .map((v) => DropdownMenuItem(value: v, child: Text(v.variantName)))
                            .toList(),
                        onChanged: _selectedModel == null
                            ? null
                            : (v) => setState(() => _selectedVariant = v),
                      ),
                    const SizedBox(height: 24),
                    if (_errorMessage != null)
                      Padding(
                        padding: const EdgeInsets.only(bottom: 12),
                        child: Text(
                          _errorMessage!,
                          style: TextStyle(color: Theme.of(context).colorScheme.error),
                        ),
                      ),
                    ElevatedButton(
                      key: const Key('next_button'),
                      onPressed: _canSubmit ? _onNext : null,
                      child: _submitting
                          ? const SizedBox(
                              height: 20,
                              width: 20,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            )
                          : const Text('Next'),
                    ),
                  ],
                ],
              ),
            ),
    );
  }
}
