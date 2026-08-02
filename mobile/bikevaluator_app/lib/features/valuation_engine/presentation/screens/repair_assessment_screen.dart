// Full Path: lib/features/valuation_engine/presentation/screens/repair_assessment_screen.dart
// Purpose: Journey step 2 - Dealer loads the Repair Component catalog and
//   selects a Repair Option (or none) per component, then submits.
// Related Documents: FS-002, ISP-002 §1.1/§2.1, EP-002 §4
import 'package:flutter/material.dart';

import '../../../../core/api_client.dart';
import '../../../../core/api_exception.dart';
import '../../data/datasources/valuation_remote_data_source.dart';
import '../../data/models/repair_component_dto.dart';
import '../controllers/valuation_controller.dart';
import '../widgets/repair_component_tile.dart';
import 'result_screen.dart';

class RepairAssessmentScreen extends StatefulWidget {
  const RepairAssessmentScreen({
    super.key,
    required this.year,
    required this.variantId,
    required this.variantLabel,
  });

  final int year;
  final String variantId;
  final String variantLabel;

  @override
  State<RepairAssessmentScreen> createState() => _RepairAssessmentScreenState();
}

class _RepairAssessmentScreenState extends State<RepairAssessmentScreen> {
  late final ValuationController _controller;

  bool _loading = true;
  bool _submitting = false;
  String? _errorMessage;
  List<RepairComponentDto> _components = [];

  /// componentId -> selected optionId (absent entry = no repair needed).
  final Map<String, String> _selections = {};

  @override
  void initState() {
    super.initState();
    _controller = ValuationController(ValuationRemoteDataSource(ApiClient()));
    _loadComponents();
  }

  Future<void> _loadComponents() async {
    setState(() {
      _loading = true;
      _errorMessage = null;
    });
    try {
      final components = await _controller.loadRepairComponents();
      setState(() {
        _components = components;
        _loading = false;
      });
    } on ApiException catch (e) {
      setState(() {
        _loading = false;
        _errorMessage = e.message;
      });
    } catch (_) {
      setState(() {
        _loading = false;
        _errorMessage = 'Network error - check your connection and try again.';
      });
    }
  }

  Future<void> _onSubmit() async {
    setState(() {
      _submitting = true;
      _errorMessage = null;
    });
    final repairAssessment = _selections.entries
        .map((e) => {'repairComponentId': e.key, 'repairOptionId': e.value})
        .toList();
    try {
      final result = await _controller.calculate(
        year: widget.year,
        variantId: widget.variantId,
        repairAssessment: repairAssessment,
      );
      if (!mounted) return;
      setState(() => _submitting = false);
      Navigator.of(context).push(
        MaterialPageRoute(builder: (_) => ResultScreen(result: result)),
      );
    } on ApiException catch (e) {
      setState(() {
        _submitting = false;
        _errorMessage = e.isPricingUnavailable
            ? 'Pricing is not available for this vehicle/year yet.'
            : e.message;
      });
    } catch (_) {
      setState(() {
        _submitting = false;
        _errorMessage = 'Network error - check your connection and try again.';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(widget.variantLabel)),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _components.isEmpty && _errorMessage == null
              ? const Center(child: Text('No repair components configured yet.'))
              : Column(
                  children: [
                    Expanded(
                      child: ListView(
                        children: [
                          for (final component in _components)
                            RepairComponentTile(
                              component: component,
                              selectedOptionId: _selections[component.id],
                              onOptionSelected: (optionId) {
                                setState(() {
                                  if (optionId == null) {
                                    _selections.remove(component.id);
                                  } else {
                                    _selections[component.id] = optionId;
                                  }
                                });
                              },
                            ),
                        ],
                      ),
                    ),
                    if (_errorMessage != null)
                      Padding(
                        padding: const EdgeInsets.all(12),
                        child: Text(
                          _errorMessage!,
                          style: TextStyle(color: Theme.of(context).colorScheme.error),
                        ),
                      ),
                    Padding(
                      padding: const EdgeInsets.all(16),
                      child: ElevatedButton(
                        key: const Key('submit_button'),
                        onPressed: _submitting ? null : _onSubmit,
                        child: _submitting
                            ? const SizedBox(
                                height: 20,
                                width: 20,
                                child: CircularProgressIndicator(strokeWidth: 2),
                              )
                            : const Text('Get Valuation'),
                      ),
                    ),
                  ],
                ),
    );
  }
}
