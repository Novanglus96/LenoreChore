<template>
  <!-- Daily reminders.
       ─────────────────────────────────────────────────────────────────────
       These write the moment you touch them -- the switch subscribes and saves,
       the time picker saves on change. That is right for a two-control setting
       and wrong to sit under a "Save changes" button that governs something
       else, which is exactly where they used to live. Split out, under a
       heading that says when they save. -->
  <div>
    <div class="d-flex align-center ga-3">
      <div class="flex-grow-1 min-width-0">
        <p class="text-subtitle-2 mb-0">Daily reminders</p>
        <p class="text-caption text-medium-emphasis mb-0">
          A daily summary of what's due and overdue.
        </p>
      </div>
      <v-switch
        v-if="pushSupported"
        v-model="notifyEnabled"
        color="primary"
        density="compact"
        hide-details
        aria-label="Daily reminders"
        :loading="notifyBusy"
        :disabled="notifyBusy"
        @update:modelValue="onToggleReminders"
      ></v-switch>
    </div>

    <div v-if="pushSupported && notifyEnabled" class="d-flex align-center ga-3 mt-3">
      <span id="remind-at-label" class="text-body-2">Remind me at</span>
      <div
        role="group"
        aria-labelledby="remind-at-label"
        class="lc-reminders__time"
      >
        <VueDatePicker
          v-model="notifyTime"
          time-picker
          auto-apply
          :teleport="true"
          @update:modelValue="onTimeChange"
        ></VueDatePicker>
      </div>
    </div>

    <p v-if="!pushSupported" class="text-caption text-medium-emphasis mb-0 mt-2">
      Not supported on this device or browser.
    </p>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import VueDatePicker from "@vuepic/vue-datepicker";
import { useChoreStore } from "@/stores/chores";
import { usePush } from "@/composables/pushComposable";

const chorestore = useChoreStore();
const showSnackbar = (text, color) => chorestore.showSnackbar(text, color);

const { isSupported, subscribe, unsubscribe, getPrefs, savePrefs } = usePush();
const pushSupported = isSupported();
const notifyEnabled = ref(false);
const notifyTime = ref({ hours: 8, minutes: 0, seconds: 0 });
const notifyBusy = ref(false);

const pad = n => String(n).padStart(2, "0");
const timeToString = t => `${pad(t.hours)}:${pad(t.minutes)}:${pad(t.seconds || 0)}`;
const stringToTime = s => {
  const [h, m, sec] = s.split(":").map(Number);
  return { hours: h || 0, minutes: m || 0, seconds: sec || 0 };
};

onMounted(async () => {
  if (!pushSupported) return;
  try {
    const prefs = await getPrefs();
    notifyEnabled.value = prefs.notify_enabled;
    if (prefs.notify_time) notifyTime.value = stringToTime(prefs.notify_time);
  } catch {
    // Leave defaults if prefs can't be loaded.
  }
});

const onToggleReminders = async value => {
  notifyBusy.value = true;
  try {
    if (value) {
      await subscribe();
      await savePrefs(true, timeToString(notifyTime.value));
      showSnackbar("Daily reminders enabled!", "success");
    } else {
      await savePrefs(false, timeToString(notifyTime.value));
      await unsubscribe();
      showSnackbar("Daily reminders disabled.", "success");
    }
  } catch (error) {
    notifyEnabled.value = !value; // revert on failure
    showSnackbar(error.message || "Could not update reminders.", "error");
  } finally {
    notifyBusy.value = false;
  }
};

const onTimeChange = async () => {
  if (!notifyEnabled.value) return;
  try {
    await savePrefs(true, timeToString(notifyTime.value));
    showSnackbar("Reminder time updated.", "success");
  } catch {
    showSnackbar("Could not update reminder time.", "error");
  }
};
</script>

<style scoped>
.lc-reminders__time {
  min-width: 150px;
}

.min-width-0 {
  min-width: 0;
}
</style>
