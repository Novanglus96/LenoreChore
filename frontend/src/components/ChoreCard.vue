<template>
  <!-- The card is an <article> with its own accessible name, so a screen
       reader can navigate the list by chore instead of hearing an unbroken run
       of unlabelled groups. -->
  <v-card
    class="lc-chore-card lc-lift"
    :class="{ 'lc-completing': isCompleting, 'lc-chore-card--idle': isIdle }"
    tag="article"
    :aria-label="cardLabel"
    :rounded="$vuetify.display.smAndDown ? 0 : 'lg'"
    :elevation="0"
    border
  >
    <!-- The area group's colour, as identity rather than as a surface. Text
         never sits on it, so its contrast is not load-bearing and users keep
         whatever colour they picked. -->
    <div
      class="lc-chore-card__stripe"
      :class="`bg-${localchore.area.group.group_color}`"
      aria-hidden="true"
    ></div>

    <div class="lc-chore-card__body">
      <div class="d-flex align-start ga-3">
        <v-avatar
          size="40"
          class="lc-chore-card__area-icon flex-shrink-0"
          :class="`text-${localchore.area.group.group_color}`"
          aria-hidden="true"
        >
          <v-icon :icon="localchore.area.area_icon" size="22"></v-icon>
        </v-avatar>

        <div class="flex-grow-1 min-width-0">
          <h3 class="text-subtitle-1 font-weight-medium lc-chore-card__title">
            {{ localchore.chore_name }}
          </h3>
          <p class="text-caption text-medium-emphasis mb-0">
            {{ localchore.area.area_name }}
            <span class="lc-visually-hidden">
              in {{ localchore.area.group.group_name }}</span
            >
          </p>
        </div>

        <!-- Due state. Overdue is carried by the word "overdue", an icon and a
             slow pulse -- not by red text alone, which is invisible to anyone
             who cannot distinguish it. -->
        <div v-if="localchore.status == 0" class="text-right flex-shrink-0">
          <v-chip
            size="small"
            :color="localchore.isOverdue ? 'filthy' : undefined"
            :variant="localchore.isOverdue ? 'flat' : 'tonal'"
            :class="{ 'lc-breathe': localchore.isOverdue }"
          >
            <v-icon
              start
              size="14"
              :icon="localchore.isOverdue ? 'mdi-alert-circle' : 'mdi-clock-outline'"
              aria-hidden="true"
            ></v-icon>
            {{ dueLabel }}
          </v-chip>
        </div>
      </div>

      <!-- Dirtiness. The percentage is spoken by the progressbar role, and the
           band name ("filthy") is redundant text so the meaning does not depend
           on the bar's colour. -->
      <div v-if="localchore.status == 0" class="mt-3">
        <v-progress-linear
          :model-value="localchore.dirtiness"
          :color="dirtBand.color"
          height="22"
          rounded
          :striped="localchore.dirtiness > 0"
          :aria-label="`${Math.ceil(localchore.dirtiness)} percent dirty, ${dirtBand.label}`"
        >
          <span class="text-caption font-weight-medium">
            {{ Math.ceil(localchore.dirtiness) }}% · {{ dirtBand.label }}
          </span>
        </v-progress-linear>
      </div>

      <v-alert
        v-else-if="localchore.status == 3"
        type="info"
        density="compact"
        class="mt-3"
        icon="mdi-island"
        text="Vacation mode — this chore is paused."
      ></v-alert>

      <div class="d-flex align-center justify-space-between mt-3 ga-2">
        <v-chip
          size="small"
          variant="tonal"
          :prepend-icon="
            localchore.assignee ? 'mdi-account-check' : 'mdi-account-outline'
          "
        >
          {{ computedAssignee }}
        </v-chip>

        <div class="d-flex align-center ga-1">
          <span class="lc-visually-hidden">Effort</span>
          <v-rating
            v-model="localchore.effort"
            :readonly="!expand"
            length="3"
            size="18"
            density="compact"
            active-color="accent"
            :item-aria-label="'Effort level {0} of 3'"
            @update:modelValue="changeDetected()"
          ></v-rating>
        </div>
      </div>
    </div>

    <v-expand-transition>
      <div v-if="expand">
        <v-container class="bg-surface-variant">
          <v-row v-if="remoteUpdatePending" dense>
            <v-col>
              <v-alert
                type="warning"
                variant="tonal"
                density="compact"
                role="status"
                aria-live="polite"
                text="Someone else changed this chore while you were editing.
                      Saving keeps your version; reset loads theirs."
              ></v-alert>
            </v-col>
          </v-row>
          <v-row dense class="bg-surface-variant">
            <v-col>
              <v-text-field
                v-model="localchore.chore_name"
                label="Chore Name"
                @update:modelValue="changeDetected()"
              ></v-text-field>
            </v-col>
          </v-row>
          <v-row dense class="bg-surface-variant">
            <v-col>
              <VueDatePicker
                v-model="localchore.lastCompleted"
                :timezone="userTimezone"
                model-type="yyyy-MM-dd"
                :enable-time-picker="false"
                auto-apply
                format="yyyy-MM-dd"
                @update:modelValue="changeDetected(true)"
              ></VueDatePicker>
            </v-col>
            <v-col>
              <VueDatePicker
                v-model="localchore.nextDue"
                :timezone="userTimezone"
                model-type="yyyy-MM-dd"
                :enable-time-picker="false"
                auto-apply
                format="yyyy-MM-dd"
                @update:modelValue="changeDetected(true)"
              ></VueDatePicker>
            </v-col>
          </v-row>
          <v-row dense>
            <v-col> Repeats </v-col>
          </v-row>
          <v-row dense>
            <v-col>
              <v-select
                label="Interval*"
                required
                :items="intervals"
                v-model="localchore.intervalNumber"
                @update:modelValue="changeDetected()"
              ></v-select>
            </v-col>
            <v-col>
              <v-select
                label="Unit(s)*"
                required
                :items="units"
                v-model="localchore.unit"
                @update:modelValue="changeDetected()"
              ></v-select>
            </v-col>
          </v-row>
          <!-- A real fieldset with a legend. These twelve controls previously
               sat loose in the form, so each announced alone with nothing
               tying it to "which months does this chore run in". -->
          <v-row dense>
            <v-col>
              <!-- Twelve checkboxes were most of the scroll between the first
                   field and the Save button on a phone, for a setting that is
                   "all year" on nearly every chore. Shared with AddChoreForm so
                   the two cannot drift. -->
              <LcMonthPicker
                v-model="localchore.active_months"
                @update:modelValue="changeDetected()"
              />
            </v-col>
          </v-row>
          <v-row dense>
            <v-col>
              <v-btn
                icon="mdi-content-save-outline"
                :aria-label="`Save changes to ${localchore.chore_name}`"
                :disabled="!saveEnabled"
                @click="callSaveChore(localchore)"
              >
                <v-icon icon="mdi-content-save-outline"></v-icon>
                <v-tooltip activator="parent" location="top">Save</v-tooltip>
              </v-btn>
              <v-btn
                icon="mdi-arrow-u-left-top-bold"
                :aria-label="`Discard changes to ${localchore.chore_name}`"
                :disabled="!saveEnabled"
                @click="callResetChore()"
              >
                <v-icon icon="mdi-arrow-u-left-top-bold"></v-icon>
                <v-tooltip activator="parent" location="top">Reset</v-tooltip>
              </v-btn>
              <LcConfirmDialog
                v-model="deleteDialog"
                title="Delete this chore?"
                icon="mdi-delete-forever-outline"
                confirm-label="Delete chore"
                confirm-icon="mdi-delete-forever-outline"
                @confirm="callDeleteChore(localchore)"
              >
                <template v-slot:activator="{ props: activatorProps }">
                  <v-btn
                    v-bind="activatorProps"
                    icon="mdi-delete-forever-outline"
                    color="filthy"
                    :aria-label="`Delete ${localchore.chore_name}`"
                  >
                    <v-icon icon="mdi-delete-forever-outline"></v-icon>
                    <v-tooltip activator="parent" location="top">
                      Delete
                    </v-tooltip>
                  </v-btn>
                </template>

                Deleting <strong>{{ localchore.chore_name }}</strong> from
                <strong>{{ localchore.area.area_name }}</strong> also removes it
                from the history. This cannot be undone.
              </LcConfirmDialog>
            </v-col>
          </v-row>
        </v-container>
      </div>
    </v-expand-transition>
    <v-expand-transition>
      <div v-if="localchore.history">
        <v-container class="bg-surface-variant">
          <v-row dense>
            <v-col>
              <v-table class="bg-surface-variant">
                <thead>
                  <tr>
                    <th class="text-left">Date</th>
                    <th class="text-left">Completed By</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="item in localchore.last_three_history_items"
                    :key="item.id"
                  >
                    <td>{{ item.completed_date }}</td>
                    <td>{{ item.completed_by }}</td>
                  </tr>
                </tbody>
              </v-table>
            </v-col>
          </v-row>
        </v-container>
      </div>
    </v-expand-transition>

    <v-divider></v-divider>

    <!-- Every control here was previously an icon with no accessible name, so
         the whole action bar announced as "button, button, button…". Each now
         states the action AND its object, and any label that changes with state
         changes with it (claim/release, disable/enable). -->
    <v-card-actions class="lc-chore-card__actions">
      <v-btn
        icon="mdi-check"
        :aria-label="`Mark ${localchore.chore_name} complete`"
        :disabled="localchore.status > 0 || expand || isCompleting"
        @click="callCompleteChore(localchore.id, getID)"
      >
        <v-icon icon="mdi-check"></v-icon>
        <v-tooltip activator="parent" location="top">Complete</v-tooltip>
      </v-btn>

      <v-dialog v-model="snooze" scrollable max-width="420px">
        <template v-slot:activator="{ props: activatorProps }">
          <v-btn
            v-bind="activatorProps"
            icon="mdi-alarm-snooze"
            :aria-label="`Snooze ${localchore.chore_name}`"
            :disabled="localchore.status > 0 || expand"
          >
            <v-icon icon="mdi-alarm-snooze"></v-icon>
            <v-tooltip activator="parent" location="top">Snooze</v-tooltip>
          </v-btn>
        </template>
        <v-card>
          <v-card-title>Snooze {{ localchore.chore_name }}</v-card-title>
          <v-divider></v-divider>
          <v-card-text>
            <!-- VueDatePicker does not render an element carrying the id its
                 `uid` prop implies, so a <label for> would point at nothing.
                 Labelling the group is what actually reaches the control. -->
            <div
              id="snooze-date-label"
              class="text-body-2 mb-2"
              aria-hidden="true"
            >
              Push the due date to
            </div>
            <div role="group" aria-labelledby="snooze-date-label">
              <VueDatePicker
                v-model="localchore.nextDue"
                :timezone="userTimezone"
                model-type="yyyy-MM-dd"
                :enable-time-picker="false"
                :dark="theme.global.current.value.dark"
                auto-apply
                teleport
                format="yyyy-MM-dd"
              ></VueDatePicker>
            </div>
          </v-card-text>
          <v-divider></v-divider>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn variant="text" @click="snooze = false">Cancel</v-btn>
            <v-btn
              variant="flat"
              color="primary"
              @click="callSnoozeChore(localchore.id, localchore.nextDue)"
            >
              Snooze
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <v-btn
        icon="mdi-clipboard-account-outline"
        :aria-label="claimLabel"
        :aria-pressed="localchore.isAssigned ? 'true' : 'false'"
        :color="localchore.isAssigned ? 'primary' : undefined"
        :disabled="localchore.status > 0 || expand"
        @click="callClaimChore(localchore.id, localchore.assignee_id)"
      >
        <v-icon
          :icon="
            localchore.isAssigned
              ? 'mdi-clipboard-account'
              : 'mdi-clipboard-account-outline'
          "
        ></v-icon>
        <v-tooltip activator="parent" location="top">{{ claimLabel }}</v-tooltip>
      </v-btn>

      <v-btn
        icon="mdi-circle-off-outline"
        :aria-label="toggleLabel"
        :aria-pressed="localchore.status == 0 ? 'false' : 'true'"
        :color="localchore.status == 0 ? undefined : 'accent'"
        :disabled="localchore.status == 3"
        @click="callToggleChore(localchore.id, localchore.status)"
      >
        <v-icon
          :icon="
            localchore.status == 0 ? 'mdi-circle-off-outline' : 'mdi-circle-outline'
          "
        ></v-icon>
        <v-tooltip activator="parent" location="top">{{ toggleLabel }}</v-tooltip>
      </v-btn>

      <v-spacer></v-spacer>

      <v-btn
        icon="mdi-clipboard-text-clock-outline"
        :aria-label="`${localchore.history ? 'Hide' : 'Show'} history for ${localchore.chore_name}`"
        :aria-expanded="localchore.history ? 'true' : 'false'"
        :color="localchore.history ? 'primary' : undefined"
        :disabled="expand"
        @click="localchore.history = !localchore.history"
      >
        <v-icon icon="mdi-clipboard-text-clock-outline"></v-icon>
        <v-tooltip activator="parent" location="top">History</v-tooltip>
      </v-btn>

      <v-btn
        :icon="expand ? 'mdi-chevron-up' : 'mdi-chevron-down'"
        :aria-label="`${expand ? 'Close' : 'Open'} editor for ${localchore.chore_name}`"
        :aria-expanded="expand ? 'true' : 'false'"
        :disabled="saveEnabled || localchore.status == 3"
        @click="expand = !expand"
      >
        <v-icon :icon="expand ? 'mdi-chevron-up' : 'mdi-chevron-down'"></v-icon>
        <v-tooltip activator="parent" location="top">
          {{ expand ? "Close editor" : "Edit" }}
        </v-tooltip>
      </v-btn>
    </v-card-actions>
  </v-card>
</template>
<script setup>
// defineProps/defineEmits are compiler macros — importing them warns on every
// build and every test run.
import { computed, ref, watch, onMounted } from "vue";
import { useChoreStore } from "@/stores/chores";
import VueDatePicker from "@vuepic/vue-datepicker";
import "@vuepic/vue-datepicker/dist/main.css";
import { useUserStore } from "@/stores/user";
import { useOptions } from "@/composables/optionsComposable";
import { useTheme } from "vuetify";
import LcMonthPicker from "@/components/LcMonthPicker.vue";
import LcConfirmDialog from "@/components/LcConfirmDialog.vue";

const theme = useTheme();

// Was hardcoded to "America/New_York" on all three pickers, so every date this
// card wrote was interpreted in Eastern time regardless of where the user
// actually is -- while the backend has stored a per-user notify_timezone since
// the reminders feature shipped. Falls back to the browser's own zone.
const userTimezone =
  Intl.DateTimeFormat().resolvedOptions().timeZone || undefined;


const { options } = useOptions();
const expand = ref(false);
const snooze = ref(false);
const saveEnabled = ref(false);
const deleteDialog = ref(false);
const chorestore = useChoreStore();
const userstore = useUserStore();
const emit = defineEmits([
  "editChore",
  "removeChore",
  "snoozeChore",
  "completeChore",
  "claimChore",
  "toggleActivation",
]);
const props = defineProps({
  chore: Object,
});
const localchore = ref({ ...props.chore });

function deepCopy(obj) {
  return JSON.parse(JSON.stringify(obj));
}

// True when a newer version of this chore arrived from the server while the
// user had unsaved edits, so we declined to apply it.
const remoteUpdatePending = ref(false);

watch(
  () => props.chore,
  updatedChore => {
    // Never overwrite unsaved edits. Every write endpoint publishes an SSE
    // event, so any other household member completing a chore invalidates
    // ["chores"] and hands this component a new object identity. Before this
    // guard that replaced the open edit panel's contents mid-typing -- and
    // because saveEnabled stayed true, the next click of Save wrote the
    // reverted values back over the server's copy.
    if (saveEnabled.value) {
      remoteUpdatePending.value = true;
      return;
    }
    localchore.value = deepCopy(updatedChore);
    remoteUpdatePending.value = false;
  },
);

onMounted(() => {
  localchore.value = deepCopy(props.chore);
});

// Reset means "discard my edits and show the server's current copy", so it
// takes a full snapshot rather than restoring the nine fields it used to name
// individually. That list omitted anything a remote change might have touched
// (assignee and status among them), which mattered once the watch above began
// holding updates back.
const callResetChore = async () => {
  localchore.value = deepCopy(props.chore);
  saveEnabled.value = false;
  remoteUpdatePending.value = false;
};
const changeDetected = async recalcDirty => {
  if (recalcDirty) {
    localchore.value.dirtiness = calcDirtiness();
    localchore.value.duedays = calcDueDays();
  }
  saveEnabled.value = true;
};
const calcDirtiness = () => {
  const millisecondsInADay = 1000 * 60 * 60 * 24;
  const today = new Date();
  const nextDueDate = new Date(localchore.value.nextDue);
  const lastCompleted = new Date(localchore.value.lastCompleted);

  // Calculate the time difference in milliseconds
  const timesincedone = lastCompleted - today;
  const timeperiod = lastCompleted - nextDueDate;

  // Calculate the time difference in days
  const timesincedonedays = Math.ceil(timesincedone / millisecondsInADay);
  const timeperioddays = Math.ceil(timeperiod / millisecondsInADay);

  let dirtiness = 0;

  if (timeperioddays === 0) {
    dirtiness = 0;
  } else {
    dirtiness = Math.round((timesincedonedays / timeperioddays) * 100);
    dirtiness = Math.min(dirtiness, 100); // Ensure dirtiness is at most 100
  }

  return dirtiness;
};
const calcDueDays = () => {
  const today = new Date();
  const nextDueDate = new Date(localchore.value.nextDue);

  // Calculate the difference in milliseconds
  const timeDifference = nextDueDate - today;

  // Convert milliseconds to days
  const millisecondsInADay = 1000 * 60 * 60 * 24;
  const duedays = Math.ceil(timeDifference / millisecondsInADay);

  return duedays;
};
const getID = computed(() => {
  return userstore.getID;
});
const units = computed(() => {
  return chorestore.units;
});
const intervals = computed(() => {
  return chorestore.intervals;
});
const callSnoozeChore = async (chore_id, next_due) => {
  emit("snoozeChore", chore_id, next_due);
  snooze.value = !snooze.value;
};
const callSaveChore = async saveChore => {
  saveEnabled.value = false;
  expand.value = false;
  // Clearing this explicitly rather than waiting for the post-save refetch to
  // do it, so the flag cannot outlive the edit it belongs to.
  remoteUpdatePending.value = false;
  emit("editChore", saveChore);
};
const callDeleteChore = async deleteChore => {
  emit("removeChore", deleteChore);
  // Explicit rather than a toggle: LcConfirmDialog leaves closing to the
  // consumer, and a toggle here would reopen the dialog if it were ever called
  // from anywhere but the open one.
  deleteDialog.value = false;
};
// ── The completion moment ───────────────────────────────────────────────────
// The payoff beat of the app. The card lifts, springs away and fades while the
// dirtiness bar drains, and only then does the mutation fire.
//
// Ordering it that way is deliberate. The parent's optimistic update removes
// this chore from the list the instant the mutation starts, which unmounts the
// component -- so emitting first means the animation never renders at all.
// Waiting ~620ms before a chore completion costs nothing and is what makes the
// moment land rather than feel like a spinner.
//
// Under prefers-reduced-motion the wait collapses to zero along with the
// animation, so nobody who has asked for less motion pays a delay for it.
const isCompleting = ref(false);

const prefersReducedMotion = () =>
  typeof window !== "undefined" &&
  typeof window.matchMedia === "function" &&
  window.matchMedia("(prefers-reduced-motion: reduce)").matches;

const callCompleteChore = async (chore_id, user_id) => {
  if (isCompleting.value) return; // a second click would emit twice
  isCompleting.value = true;

  // Drain the bar in step with the card leaving.
  localchore.value.dirtiness = 0;

  const beat = prefersReducedMotion() ? 0 : 620; // keep in step with --lc-dur-celebrate
  if (beat) await new Promise(resolve => setTimeout(resolve, beat));

  emit("completeChore", chore_id, user_id);
};
const callClaimChore = async (chore_id, user_id) => {
  let assignee = null;
  if (getID.value == user_id) {
    assignee = null;
  } else {
    assignee = getID.value;
  }
  emit("claimChore", chore_id, assignee);
};
const callToggleChore = async (chore_id, active) => {
  emit("toggleActivation", chore_id, active);
};
// The dirtiness band, carrying BOTH a colour and a word. Colour alone was the
// only signal before, which fails for anyone who cannot distinguish the hues --
// and the thresholds are user-configurable, so the word is also the only thing
// that explains why a given percentage is "filthy" in this household.
const dirtBand = computed(() => {
  const dirt = localchore.value?.dirtiness ?? 0;
  const med = options.value?.med_thresh ?? 49;
  const high = options.value?.high_thresh ?? 74;

  if (dirt <= med) return { color: "clean", label: "clean-ish" };
  if (dirt <= high) return { color: "soiled", label: "getting there" };
  return { color: "filthy", label: "filthy" };
});

const dueLabel = computed(() => {
  const days = localchore.value?.duedays ?? 0;
  if (days < 0) {
    const overdue = Math.abs(days);
    return `${overdue} day${overdue === 1 ? "" : "s"} overdue`;
  }
  if (days === 0) return "Due today";
  if (days === 1) return "Due tomorrow";
  return `Due in ${days} days`;
});

// State-dependent labels, so what a screen reader announces changes with the
// control rather than describing only its resting state.
const claimLabel = computed(() =>
  localchore.value?.isAssigned
    ? `Release ${localchore.value.chore_name}`
    : `Claim ${localchore.value?.chore_name}`
);

const toggleLabel = computed(() =>
  localchore.value?.status == 0
    ? `Disable ${localchore.value.chore_name}`
    : `Enable ${localchore.value?.chore_name}`
);

// The card's own accessible name, so the list can be navigated chore by chore.
const cardLabel = computed(() => {
  const c = localchore.value;
  if (!c) return "Chore";
  return `${c.chore_name}, ${c.area?.area_name}, ${Math.ceil(
    c.dirtiness
  )} percent dirty, ${dueLabel.value}`;
});

// Idle = nothing pending, nothing open. Used only to allow the hover lift,
// which would be distracting while the editor is open.
const isIdle = computed(() => !expand.value && !localchore.value?.history);
const computedAssignee = computed(() => {
  if (!localchore.value) {
    return "";
  }
  if (!localchore.value.assignee_id) {
    return "Unassigned";
  }
  if (!localchore.value.assignee.fullname) {
    return localchore.value.assignee.email;
  } else {
    if (localchore.value.assignee.fullname == " ") {
      return localchore.value.assignee.email;
    } else {
      return localchore.value.assignee.fullname;
    }
  }
});
</script>
<style scoped>
.lc-chore-card {
  position: relative;
  overflow: hidden;
  background: rgb(var(--v-theme-surface));
}

/* The area group's colour. 4px is enough to identify at a glance in a scrolling
   list without becoming a block of colour competing with the content. */
.lc-chore-card__stripe {
  position: absolute;
  inset-block: 0;
  inset-inline-start: 0;
  width: 4px;
}

.lc-chore-card__body {
  /* Clears the stripe so text never sits against it. */
  padding: var(--lc-space-4) var(--lc-space-4) var(--lc-space-3)
    calc(var(--lc-space-4) + 4px);
}

.lc-chore-card__area-icon {
  background: rgb(var(--v-theme-surface-variant));
}

/* Long chore names wrap rather than pushing the due chip off the card. */
.lc-chore-card__title {
  line-height: 1.3;
  overflow-wrap: anywhere;
}

.min-width-0 {
  /* Flex children default to min-width:auto, which stops them shrinking below
     their content and is what lets a long word overflow the card. */
  min-width: 0;
}

/* The lift is for cards at rest. While the editor or history panel is open the
   card is a working surface, and having it rise under the pointer is noise. */
.lc-chore-card:not(.lc-chore-card--idle) {
  transform: none !important;
  box-shadow: none !important;
}

.lc-chore-card__actions {
  padding-inline: var(--lc-space-2);
}



@media (max-width: 599px) {
  .lc-chore-card__body {
    padding: var(--lc-space-3) var(--lc-space-3) var(--lc-space-2)
      calc(var(--lc-space-3) + 4px);
  }

  /* Vuetify's default icon-button hit area dips under the 44px that both
     WCAG 2.5.8 and the platform HIGs ask for on touch. */
  .lc-chore-card__actions :deep(.v-btn--icon) {
    min-width: 44px;
    min-height: 44px;
  }
}
</style>
